from aiosqlite import Connection, Row
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel
from starlette.responses import Response

from achievements import AchievementSystem
from api.auth import authorize
from config import AppConfig, get_config
from db import delete_image, get_db, make_static_url, owns_plant

router = APIRouter(prefix="/plants")


class PlantSchema(BaseModel):
    id: int
    name: str
    image_url: str | None

    @staticmethod
    def from_row(row: Row) -> "PlantSchema":
        return PlantSchema(id=row["ID"], name=row["Name"], image_url=row["ImageURL"])


@router.get("", response_model=list[PlantSchema])
async def get_plants(
    user_id: int = Depends(authorize), db: Connection = Depends(get_db)
) -> list[PlantSchema]:
    async with db.execute_fetchall(
        """
        SELECT Plants.ID as ID, Name, URL as ImageURL FROM Plants
        LEFT JOIN Images ON Plants.ImageID = Images.ID
        WHERE UserID = ?
    """,
        (user_id,),
    ) as plants:
        return [PlantSchema.from_row(row) for row in plants]


@router.get("/{plant_id}", response_model=PlantSchema)
async def get_plant(
    plant_id: int, user_id: int = Depends(authorize), db: Connection = Depends(get_db)
) -> PlantSchema:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(
            status_code=401, detail="Plant does not belong to this user"
        )

    async with db.execute(
        """
       SELECT Plants.ID as ID, Name, URL as ImageURL FROM Plants
        LEFT JOIN Images ON Plants.ImageID = Images.ID
       WHERE Plants.ID = ?
    """,
        (plant_id,),
    ) as cursor:
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Plant does not exist")
        return PlantSchema.from_row(row)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PlantSchema)
async def add_plant(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    picture: UploadFile | None = File(None),
    user_id: int = Depends(authorize),
    config: AppConfig = Depends(get_config),
    db: Connection = Depends(get_db),
    achievements: AchievementSystem = Depends(AchievementSystem),
) -> PlantSchema:
    image_id: int | None = None
    url: str | None = None
    if picture is not None and picture.size != 0:
        url, delete_url = await make_static_url(config.imgbb_key, picture)
        if (
            row := await db.execute_insert(
                "INSERT INTO Images(URL, DeleteURL) VALUES (?, ?)", (url, delete_url)
            )
        ) is None:
            raise HTTPException(
                status_code=500, detail="Failed to create image resource"
            )
        image_id = row[0]

    if (
        row := await db.execute_insert(
            "INSERT INTO Plants(Name, UserID, ImageID) VALUES (?, ?, ?)",
            (name, user_id, image_id),
        )
    ) is None:
        raise HTTPException(status_code=500, detail="Failed to create plant")

    plant_id = row[0]

    await db.commit()
    background_tasks.add_task(
        achievements.plant_achievements, user_id
    )  # use background task just in case achievements become slower
    return PlantSchema(id=plant_id, name=name, image_url=url)


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant_id: int, user_id: int = Depends(authorize), db: Connection = Depends(get_db)
) -> Response:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(
            status_code=404, detail="Plants does not belong to this user"
        )

    await delete_image(plant_id, db)
    await db.execute("DELETE FROM Plants WHERE ID = ?", (plant_id,))
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
