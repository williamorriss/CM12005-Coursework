from typing import AsyncIterable

from aiosqlite import Connection
from fastapi import APIRouter, Depends, status
from fastapi.sse import EventSourceResponse
from pydantic import BaseModel
from starlette.responses import JSONResponse

from achievements import AchievementCode, AchievementEvent, AchievementSystem
from api.auth import authorize
from db import get_db
from achievements import _plantcount_achievements

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

@router.get(
    "/stream",
    response_class=EventSourceResponse,
    responses={
        200: {
            "model": AchievementSchema,
            "description": "SSE for new achievements",
        }
    },
)
async def subscribe_achievements(
    user_id: int = Depends(authorize),
    achievements: AchievementSystem = Depends(AchievementSystem),
) -> AsyncIterable[AchievementSchema]:
    """
    Method to create a
    """
    queue = achievements.create_listener(user_id)
    try:
        while True:
            event = await queue.get()
            yield AchievementSchema.from_event(event)
    finally:
        achievements.remove_listener(user_id, queue)


@router.post("/test")
async def test(
    user_id: int = Depends(authorize),
    achievements: AchievementSystem = Depends(AchievementSystem),
    db: Connection = Depends(get_db),
) -> JSONResponse:
    await _plantcount_achievements(db, user_id)
    achievements.send(user_id, AchievementEvent(AchievementCode.P10))
    return JSONResponse(content="posted", status_code=status.HTTP_200_OK)

@router.get("", response_model=list[AchievementSchema])
async def list_achievements(
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db),
) -> list[AchievementSchema]:
    rows = await db.execute_fetchall(
        """
        SELECT a.Code as Code FROM Awards a
        INNER JOIN Achievements ac ON a.ID = ac.AwardID
        WHERE ac.UserID = ?""",
        (user_id,),
    )

    return [AchievementSchema(code=row["Code"]) for row in rows]


@router.delete("")
async def delete_achievements(
    user_id: int = Depends(authorize), db: Connection = Depends(get_db)
) -> JSONResponse:
    await db.execute("DELETE FROM achievements WHERE UserID = ?", (user_id,))
    return JSONResponse(content="deleted", status_code=status.HTTP_200_OK)
