from pydantic import BaseModel, Field

class LoginRequestDTO(BaseModel):
    username: str = Field(
        ..., 
        description="The user's identifier (email, phone, or username)",
        examples=["user@example.com", "+525512345678", "admin_user"]
    )
    password: str = Field(
        ..., 
        description="The user's secret password",
        examples=["MySecurePass123!"]
    )

class UserInfoDTO(BaseModel):
    email: str = Field(..., examples=["user@example.com"])

class LoginResponseDTO(BaseModel):
    message: str = Field(..., examples=["Login successful"])
    user: UserInfoDTO
