from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import datetime
from datetime import timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

from database import get_user, get_user_by_id # Assuming get_user is still in database.py
import os

# Security
# Load secret from environment; fallback is for dev only
SECRET_KEY = os.getenv("SECRET_KEY", "dev_insecure_secret_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    is_admin: Optional[int] = 0 # Added is_admin
    tenant_id: Optional[int] = None
    is_super_admin: Optional[int] = 0
    audience_type: Optional[str] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    is_admin: int = 0
    expires_in: int
    is_super_admin: Optional[int] = 0
    name: Optional[str] = None
    username: Optional[str] = None

class TokenData(BaseModel):
    id: Optional[str] = None # Changed from username to id
    tenant_id: Optional[int] = None
    audience_type: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, audience_type: Optional[str] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    if audience_type:
        to_encode.update({"audience_type": audience_type})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"DEBUG: Token created: {encoded_jwt} with payload: {to_encode})")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    print(f"DEBUG: get_current_user received token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG: get_current_user decoded payload: {payload}")
        user_id: str = payload.get("sub") # Extract user_id
        tenant_id: int = payload.get("tenant_id") # Extract tenant_id
        audience_type: Optional[str] = payload.get("audience_type") # Extract audience_type
        if user_id is None:
            print(f"DEBUG: get_current_user - user_id missing in payload: user_id={user_id}, tenant_id={tenant_id}")
            raise credentials_exception
        token_data = TokenData(id=user_id, tenant_id=tenant_id, audience_type=audience_type) # Use id, tenant_id, and audience_type

        user = get_user_by_id(int(user_id), tenant_id=tenant_id)
        print(f"DEBUG: get_current_user - user retrieved from DB: {user}")
        if user is None:
            print(f"DEBUG: get_current_user - User not found in DB for user_id: {user_id}")
            raise credentials_exception
        # Convert sqlite3.Row to a dictionary
        return dict(user)

    except JWTError as e:
        print(f"DEBUG: get_current_user JWTError: {e}")
        raise credentials_exception

async def get_user_from_expired_token(token: str = Depends(oauth2_scheme)):
    print(f"DEBUG: get_user_from_expired_token received token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials for expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        print(f"DEBUG: get_user_from_expired_token decoded payload: {payload}")
        user_id: str = payload.get("sub")
        tenant_id: int = payload.get("tenant_id")
        audience_type: Optional[str] = payload.get("audience_type") # Extract audience_type
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id, tenant_id=tenant_id, audience_type=audience_type)
    except JWTError as e:
        print(f"DEBUG: get_user_from_expired_token JWTError: {e}")
        raise credentials_exception
    user = get_user_by_id(user_id=int(token_data.id), tenant_id=token_data.tenant_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    print(f"DEBUG: get_current_admin_user received user: {current_user}")
    if not (current_user.get("is_admin") == 1 or current_user.get("is_super_admin") == 1):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user
