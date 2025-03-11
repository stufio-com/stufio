from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from motor.core import AgnosticDatabase
from odmantic import AIOEngine

from stufio.db.mongo_base import MongoBase
from stufio.db.mongo import get_engine

from stufio.core.config import get_settings

settings = get_settings()
ModelType = TypeVar("ModelType", bound=MongoBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDMongoBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.engine: AIOEngine = get_engine()

    async def get(self, db: AgnosticDatabase, id: Any) -> Optional[ModelType]:
        return await self.engine.find_one(self.model, self.model.id == id)

    async def get_multi(self, db: AgnosticDatabase, *, page: int = 0, page_break: bool = False) -> list[ModelType]:
        offset = {"skip": page * settings.MULTI_MAX, "limit": settings.MULTI_MAX} if page_break else {}
        return await self.engine.find(self.model, **offset)

    async def create(self, db: AgnosticDatabase, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        return await self.engine.save(db_obj)

    async def update(
        self, db: AgnosticDatabase, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        # TODO: Check if this saves changes with the setattr calls
        await self.engine.save(db_obj)
        return db_obj

    async def remove(self, db: AgnosticDatabase, *, id: int) -> ModelType:
        obj = await self.model.get(id)
        if obj:
            await self.engine.delete(obj)
        return obj
