from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List
from uuid import UUID
from datetime import date


class BaseSchema(BaseModel):
    @property
    def as_db_dict(self):
        to_db = self.model_dump(exclude_defaults=True, exclude_none=True, exclude={"identifier, id"})
        for key in ["id", "identifier"]:
            if key in self.model_dump().keys():
                to_db[key] = self.model_dump()[key].hex
        return to_db


class MetadataBaseSchema(BaseSchema):
    # Receive via API
    # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#section-3
    title: Optional[str] = Field(None, description="A human-readable title given to the resource.")
    description: Optional[str] = Field(
        None,
        description="A short description of the resource.",
    )
    isActive: Optional[bool] = Field(default=True, description="Whether the resource is still actively maintained.")
    isPrivate: Optional[bool] = Field(
        default=True,
        description="Whether the resource is private to team members with appropriate authorisation.",
    )


class MetadataBaseCreate(MetadataBaseSchema):
    pass


class MetadataBaseUpdate(MetadataBaseSchema):
    identifier: UUID = Field(..., description="Automatically generated unique identity for the resource.")


class MetadataBaseInDBBase(MetadataBaseSchema):
    # Identifier managed programmatically
    identifier: UUID = Field(..., description="Automatically generated unique identity for the resource.")
    created: date = Field(..., description="Automatically generated date resource was created.")
    isActive: bool = Field(..., description="Whether the resource is still actively maintained.")
    isPrivate: bool = Field(
        ...,
        description="Whether the resource is private to team members with appropriate authorisation.",
    )

    class Config:
        # https://github.com/samuelcolvin/pydantic/issues/1334#issuecomment-745434257
        # Call PydanticModel.from_orm(dbQuery)
        from_attributes = True


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int

