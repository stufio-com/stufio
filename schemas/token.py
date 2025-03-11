from typing import Optional
from pydantic import BaseModel
from odmantic import Model, ObjectId


class RefreshTokenBase(BaseModel):
    token: str
    authenticates: Optional[Model] = None


class RefreshTokenCreate(RefreshTokenBase):
    authenticates: Model


class RefreshTokenUpdate(RefreshTokenBase):
    pass


class RefreshToken(RefreshTokenUpdate):
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[ObjectId] = None
    refresh: Optional[bool] = False
    totp: Optional[bool] = False


class MagicTokenPayload(BaseModel):
    sub: Optional[str] = None
    fingerprint: Optional[str] = None


class WebToken(BaseModel):
    claim: str
