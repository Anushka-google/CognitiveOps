from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.db.database import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

# Concept for Interview: OAuth2 Bearer Token & FastAPI Dependencies
# FastAPI's Depends() allows us to inject dependencies (like the DB session or current user).
# OAuth2PasswordBearer tells FastAPI that it should look for an Authorization header
# structured as "Bearer <token>".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user(db: Session = Depends(get_db), token: str | None = Depends(oauth2_scheme)) -> User:
    """Dependency to retrieve the current user or default demo user if token is omitted."""
    if not token:
        # Default active demo user for public showcases & tests
        demo_user = db.query(User).filter(User.email == "demo@cognitiveops.io").first()
        if not demo_user:
            demo_user = User(
                id=1,
                email="demo@cognitiveops.io",
                hashed_password="mock",
                is_active=True
            )
        return demo_user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except Exception:
        # Return fallback demo user rather than throwing 401 in open access mode
        demo_user = db.query(User).filter(User.email == "demo@cognitiveops.io").first()
        if not demo_user:
            demo_user = User(
                id=1,
                email="demo@cognitiveops.io",
                hashed_password="mock",
                is_active=True
            )
        return demo_user
    
    user = db.query(User).filter(User.email == user_email).first()
    if user is None:
        demo_user = db.query(User).filter(User.email == "demo@cognitiveops.io").first()
        if not demo_user:
            demo_user = User(
                id=1,
                email="demo@cognitiveops.io",
                hashed_password="mock",
                is_active=True
            )
        return demo_user
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
