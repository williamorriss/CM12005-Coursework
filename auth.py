# Bath auth w/ CAS. Here are the docs or just trust me ;-;
# https://unicon.github.io/cas/development/protocol/CAS-Protocol-V2-Specification.html

from fastapi import APIRouter, Request, Depends
from extract import *
import jwt
import base64
from fastapi.responses import RedirectResponse
import xml.etree.ElementTree as ET
from fastapi import HTTPException
import httpx

router = APIRouter(prefix="/auth")

@router.get("/login")
async def login(
    redirect: str,
    origin: str = Depends(get_origin),
    cas_origin: str = Depends(get_cas_origin),
    allowed_origins: list[str] = Depends(get_allowed_origins),
):
    try:
        redirect_url = httpx.URL(redirect)
        if strip_origin(redirect_url) not in allowed_origins:
            raise HTTPException(status_code=400, detail="Bad origin")
    except httpx.InvalidURL:
        raise HTTPException(status_code=400, detail="Redirect is not a valid URL")

    redirect64 = (base64.urlsafe_b64encode(redirect.encode("utf-8")).decode("utf-8"))

    # redirect url treated as a resource to avoid complications with cas adding queries
    # whilst still wanting an exact url ( just trust me )
    # Base64 is used to avoid annoying http url escaping
    callback = f"{origin}/auth/cas/{redirect64}"
    return RedirectResponse(
        url=f"{cas_origin}/login?service={callback}",
        status_code=302
    )

@router.get("/logout")
async def logout(cas_origin: str = Depends(get_cas_origin)):
    # Redirects to CAS logout page.
    # Unfortunately it does not seem like Bath CAS implements the
    # return link so you will stranded on the logout page
    return RedirectResponse(url=f"{cas_origin}/logout", status_code=303)

@router.get("/cas/{redirect64}")
async def cas_callback(
    redirect64: str,
    ticket: str,
    allowed_origins: list[str] = Depends(get_allowed_origins),
    origin: str = Depends(get_origin),
    cas_origin: str = Depends(get_cas_origin),
    db: Connection = Depends(get_db),
):
    try:
        redirect_url = base64.urlsafe_b64decode(redirect64).decode("utf-8")
        redirect = httpx.URL(redirect_url)
        if strip_origin(redirect) not in allowed_origins:
            raise HTTPException(status_code=400, detail="Bad origin")
    except httpx.InvalidURL:
        raise HTTPException(status_code=400, detail="Redirect is not a valid URL")

    try:
        username = await get_username(redirect64, ticket, origin, cas_origin)
        if (user_id := await get_user_id(db, username)) is None:
            if (user_id := await create_user(db, username)) is None:
                raise HTTPException(status_code=500, detail="Failed to create new user")

        token = jwt.encode({user_id: user_id}, key="PleaseChangeLater", algorithm="HS256")

        response = RedirectResponse(url=redirect, status_code=302)
        response.set_cookie(key="auth-token", httponly=True, value=token,)

        return response

    except HTTPException as http_err:
        print(http_err.detail)
        raise http_err

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="Server error")

async def get_username(
    redirect64: str,
    ticket: str,
    origin: str,
    cas_origin: str
) -> str:
    async with httpx.AsyncClient(base_url=cas_origin) as cas_client:
        service = f"{origin}/auth/cas/{redirect64}"
        response = await cas_client.get(f"/serviceValidate?service={service}&ticket={ticket}")

    namespace = {"cas": "http://www.yale.edu/tp/cas"}
    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        raise HTTPException(status_code=502, detail="Bad CAS response")

    if (failure := root.find("cas:authenticationFailure", namespace)) is not None:
        error = failure.findtext("cas:message", namespaces=namespace)
        print(error)
        raise HTTPException(status_code=401, detail="Failed to authenticate")

    if (success := root.find("cas:authenticationSuccess", namespace)) is None:
        raise HTTPException(status_code=500, detail="No CAS response")

    if (user := success.findtext("cas:user", namespaces=namespace) ) is None:
        raise HTTPException(status_code=500, detail="Server error whilst parsing CAS response")

    return user

async def get_user_id(db: Connection, username: str) -> int | None:
    async with db.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else None

async def create_user(db: Connection, username: str) -> int | None:
    cursor = await db.execute(
        "INSERT INTO users (username) VALUES (?)",
        (username,)
    )
    await db.commit()
    return cursor.lastrowid


def strip_origin(url: httpx.URL) -> str:
    return str(url.join('/')).rstrip('/')