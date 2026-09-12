from pydantic import BaseModel, EmailStr

# Concept for Interview: Pydantic Validation & Separation of Concerns
# We separate the DB Model (SQLAlchemy) from the API Schema (Pydantic).
# This prevents accidentally exposing sensitive fields (like hashed_password) in API responses.

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
