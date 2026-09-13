from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post(
    "/signup", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "User with this email already exists"}
    }
)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user for CognitiveOps.

    Concept for Interview: Unique Constraints & Idempotency.
    We check if the email exists to enforce unique constraints at the application level 
    before trying to insert to avoid raw Database IntegrityErrors.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post(
    "/login", 
    response_model=Token,
    summary="Login for an Access Token",
    responses={
        200: {"description": "Successfully authenticated and returns a JWT"},
        401: {"description": "Incorrect email or password"}
    }
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate and receive a JWT access token.
    
    Concept for Interview: Form Data vs JSON
    OAuth2 spec specifically requires password credentials to be sent as form data 
    (application/x-www-form-urlencoded), not JSON. This is why we use OAuth2PasswordRequestForm.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # the subject "sub" of the token is the user's email or ID
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
