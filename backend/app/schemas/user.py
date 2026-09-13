from pydantic import BaseModel, EmailStr

# Concept for Interview: Pydantic Validation & Separation of Concerns
# We separate the DB Model (SQLAlchemy) from the API Schema (Pydantic).
# This prevents accidentally exposing sensitive fields (like hashed_password) in API responses.

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "admin@cognitiveops.io",
                    "password": "securepassword123!"
                }
            ]
        }
    }

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "email": "admin@cognitiveops.io",
                    "is_active": True
                }
            ]
        }
    }

class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                }
            ]
        }
    }
