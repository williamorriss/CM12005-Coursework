# Bath auth w/ CAS. Here are the docs or just trust me ;-;
# https://unicon.github.io/cas/development/protocol/CAS-Protocol-V2-Specification.html
from aiosqlite import Connection, OperationalError
from db import get_db
from fastapi.requests import Request
from fastapi import APIRouter, Depends
import jwt
import base64
from fastapi.responses import RedirectResponse, Response
import xml.etree.ElementTree as ET
from fastapi import HTTPException
import httpx
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/auth")

class UserSession(BaseModel):
    user_id: int
    username: str


# extractors
def get_allowed_origins(request: Request) -> list[str]:
    return request.app.state.ALLOWED_ORIGINS

def get_cas_origin(request: Request) -> str:
    return request.app.state.CAS_ORIGIN

def get_origin(request: Request) -> str:
    return request.app.state.ORIGIN

def get_auth_key(request: Request) -> str:
    return request.app.state.KEY

def authorize(request: Request) -> int:
    auth_token = request.cookies.get("auth-token")
    if auth_token is None:
        raise HTTPException(status_code=401, detail="No auth token")

    try:
        claims = jwt.decode(
            jwt=auth_token,
            key=get_auth_key(request),
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid auth token")

    return claims["user_id"]

# endpoints

@router.get("/login", response_class=RedirectResponse)
async def login(
    redirect: str,
    origin: str = Depends(get_origin),
    cas_origin: str = Depends(get_cas_origin),
    allowed_origins: list[str] = Depends(get_allowed_origins),
) -> RedirectResponse:
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
    callback = f"{origin}/api/auth/cas/{redirect64}"
    return RedirectResponse(
        url=f"{cas_origin}/login?service={callback}",
        status_code=302
    )

@router.get("/logout", response_class=RedirectResponse)
async def logout(cas_origin: str = Depends(get_cas_origin)) -> RedirectResponse:
    response = RedirectResponse(url=f"{cas_origin}/logout", status_code=302)
    response.delete_cookie("auth-token")
    return response

@router.get("/cas/{redirect64}", response_class=RedirectResponse)
async def cas_callback(
    redirect64: str,
    ticket: str,
    allowed_origins: list[str] = Depends(get_allowed_origins),
    origin: str = Depends(get_origin),
    cas_origin: str = Depends(get_cas_origin),
    db: Connection = Depends(get_db),
    auth_key = Depends(get_auth_key)
) -> RedirectResponse:
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

        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        token = jwt.encode(
            {"user_id": user_id, "exp" : int(expires.timestamp())},
            key=auth_key,
            algorithm="HS256"
        )

        response = RedirectResponse(url=str(redirect), status_code=302)
        response.set_cookie(
            key="auth-token",
            value=token,
            httponly=True,
            secure=False,    # set true if deploying
            samesite="lax",
            expires=expires,
        )

        return response

    except HTTPException as http_err:
        print(http_err.detail)
        raise http_err

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="Server error")



@router.get("/session", response_model=UserSession)
async def retrieve_session(user_id: int = Depends(authorize), db: Connection = Depends(get_db)) -> UserSession:
    async with db.execute("SELECT username FROM users WHERE id = ?", (user_id,)) as cursor:
        row = await cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="User not found")

    username = row[0]
    return UserSession(user_id=user_id, username=username)

@router.get("/refresh", response_class=Response)
async def refresh_token(auth_key: str = Depends(get_auth_key), user_id: int = Depends(authorize)) -> Response:
    expires = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"user_id": user_id, "exp" : int(expires.timestamp())},
        key=auth_key,
        algorithm="HS256"
    )

    response = Response(status_code=200)
    response.set_cookie(
        key="auth-token",
        value=token,
        httponly=True,
        secure=False,    # set true if deploying
        samesite="lax",
        expires=expires,
    )

    return response

@router.get("/delete", response_class=RedirectResponse)
async def delete_user(
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db),
    cas_origin: str = Depends(get_cas_origin)
) -> RedirectResponse:
    try:
        async with db.execute("DELETE FROM users WHERE id = ?",(user_id,)) as cursor:
            await db.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")

        response = RedirectResponse(url=f"{cas_origin}/logout", status_code=302)
        response.delete_cookie("auth-token")
        return response

    except OperationalError:
        raise HTTPException(status_code=500, detail="Server error")

async def get_username(
        redirect64: str,
        ticket: str,
        origin: str,
        cas_origin: str
) -> str:
    async with httpx.AsyncClient(base_url=cas_origin) as cas_client:
        service = f"{origin}/api/auth/cas/{redirect64}"
        response = await cas_client.get(f"/serviceValidate?service={service}&ticket={ticket}")

    namespaces = {"cas": "http://www.yale.edu/tp/cas"}
    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        raise HTTPException(status_code=502, detail="Bad CAS response")

    if (failure := root.find("cas:authenticationFailure", namespaces)) is not None:
        error = failure.findtext("cas:message", namespaces=namespaces)
        print(error)
        raise HTTPException(status_code=401, detail="Failed to authenticate")

    if (success := root.find("cas:authenticationSuccess", namespaces)) is None:
        raise HTTPException(status_code=500, detail="No CAS response")

    if (user := success.findtext("cas:user", namespaces=namespaces) ) is None:
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
    async with db.execute("INSERT INTO users (username) VALUES (?)", (username,)) as cursor:
        await db.commit()
        return cursor.lastrowid

def strip_origin(url: httpx.URL) -> str:
    return str(url.join('/')).rstrip('/')