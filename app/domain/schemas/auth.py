from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class TokenResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
