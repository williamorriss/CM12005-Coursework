# Bath auth w/ CAS. Here are the docs or just trust me ;-;
# https://unicon.github.io/cas/development/protocol/CAS-Protocol-V2-Specification.html

import main
from fastapi import APIRouter
import asyncio
from starlette.responses import RedirectResponse, Response
import xml.etree.ElementTree as ET
from fastapi import HTTPException
import httpx
from uuid import UUID, uuid4

router = APIRouter(prefix="/auth")

CAS_ORIGIN: str = "https://auth.bath.ac.uk"

class TTLDict:
    """
    Basic Time To Live Dictionary
    (Removes values after a certain amount of time)
    Probably not the most performant thing ever, but a good thing
    for testing + we can specialise this for urls specifically etc
    """
    _TTL: int = 3600
    _lock: asyncio.Lock
    _data: dict[UUID, httpx.URL]

    def __init__(self):
        self._lock = asyncio.Lock()
        self._data = dict()

    async def insert(self, value: httpx.URL) -> UUID:
        key = uuid4()
        async with self._lock:
            self._data[key] = value

        asyncio.create_task(self._expire(key))
        return key

    async def _expire(self, key):
        await asyncio.sleep(self._TTL)
        await self.try_pop(key)

    async def try_pop(self, key) -> httpx.URL | None:
        async with self._lock:
            if key not in self._data:
                return None

            return self._data.pop(key)

redirects = TTLDict()

@router.get("/login")
async def login(redirect: str):
    try:
        redirect_url = httpx.URL(redirect)
    except httpx.InvalidURL:
        raise HTTPException(status_code=400, detail="redirect is not a valid URL")

    redirect_id = await redirects.insert(redirect_url)
    callback = f"{main.ORIGIN}/auth/cas/{redirect_id}"
    return RedirectResponse(
        url=f"{CAS_ORIGIN}/login?service={callback}",
        status_code=303
    )

@router.get("/logout")
async def logout():
    # Server logout goes here
    return RedirectResponse(url=f"{CAS_ORIGIN}/logout", status_code=303)

@router.get("/cas/{redirect_uuid}")
async def cas_callback(redirect_uuid: UUID, ticket: str):
    redirect_url = await redirects.try_pop(redirect_uuid)
    if redirect_url is None:
        raise HTTPException(status_code=400, detail="redirect uuid not recognised")

    async with httpx.AsyncClient(base_url=CAS_ORIGIN) as cas_client:
        service = f"{main.ORIGIN}/auth/cas/{redirect_uuid}"
        response = await cas_client.get(f"/serviceValidate?service={service}&ticket={ticket}")
        namespace = {"cas": "http://www.yale.edu/tp/cas"}
        root = ET.fromstring(response.text)
        if (failure := root.find("cas:authenticationFailure", namespace)) is not None:
            error = failure.findtext("cas:message", namespaces=namespace)
            print(error)
            raise HTTPException(status_code=401, detail="Failed to authenticate")

        if (success := root.find("cas:authenticationSuccess", namespace)) is None:
            raise HTTPException(status_code=500, detail="No CAS response")

        username = success.findtext("cas:user", namespaces=namespace)
        # Server auth init goes here
        return Response(status_code=200, content=f"Hello {username}")