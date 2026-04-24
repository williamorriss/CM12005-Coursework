from typing import cast, AsyncIterable

from aiosqlite import Connection
from fastapi import Request
from db import get_db

from fastapi.sse import EventSourceResponse
from pydantic import BaseModel
from starlette.responses import JSONResponse

from achievements import AchievementEvent, AchievementSystem
from fastapi import APIRouter, Depends, status
from api.auth import authorize

router = APIRouter(prefix="/achievements")

class AchievementSchema(BaseModel):
    """
    Schema for achievement data from backend -> frontend.
    """
    code: str

    @staticmethod
    def from_event(event: AchievementEvent) -> "AchievementSchema":
        """
        Constructor to turn an AchievementEvent (internal representation) -> AchievementSchema (api schema).
        Args:
            event: AchievementEvent internal achievement object created by a route when the conditions for an 
                achievement are met.

        Returns:
            New AchievementSchema instance from event.
        """
        return AchievementSchema(code=event.code)


def get_imgbb_api_key(request: Request) -> str:
    """
    Dependency injection method to get the (ImgBB)[https://imgbb.com/] api key from the current app state.
    """
    return cast(str, request.app.state.IMGBB_API_KEY)

@router.get(
    "/stream",
    response_class=EventSourceResponse,
    responses={
        200: {
            "model": AchievementSchema,
            "description": "SSE for new achievements",
        }
    }
)
async def subscribe_achievements(
    user_id: int = Depends(authorize),
    achievements: AchievementSystem = Depends(AchievementSystem),
) -> AsyncIterable[AchievementSchema]:
    """
    Method to create a 
    """
    uuid, queue = achievements.create_listener(user_id)
    try:
        while True:
            event = await queue.get()
            yield AchievementSchema.from_event(event)
    finally:
        achievements.remove_listener(user_id, uuid)

@router.post("/test")
async def test (
    user_id: int = Depends(authorize),
    achievements: AchievementSystem = Depends(AchievementSystem),
) -> JSONResponse:
    await achievements.send(user_id, AchievementEvent("test"))
    print("test achievement")
    return JSONResponse(content="posted", status_code=status.HTTP_200_OK)

@router.delete("")
async def delete_achievements(
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db)
) -> JSONResponse:
    await db.execute("DELETE FROM achievements WHERE UserID = ?", (user_id,))
    return JSONResponse(content="deleted", status_code=status.HTTP_200_OK)
