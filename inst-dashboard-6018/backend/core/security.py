from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from ..core.config import settings
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Use standard verify. 
    # If bcrypt is broken, this will still fail, but we've fixed the truncation.
    # If the issue was diagnostic-test-triggering, passing a correctly truncated string *might* solve it.
    return pwd_context.verify(plain_password[:72], hashed_password)

import hashlib
import base64
import binascii
import os
import sys
import os
# Point to the backend directory where online_exam_db_connector resides
# The file is at E:\questionretrieval\new-q-bank\backend\online_exam_db_connector.py
sys.path.append(r"E:\questionretrieval\new-q-bank\backend")
from online_exam_db_connector import php_string_encrypt

# The secret key for String::encrypt is used in TAMS and was revealed in logs
ENCRYPTION_KEY = "cbb61b96b5b2fb96a140b4be9e25a4cc"

def php_encrypt(string, key=ENCRYPTION_KEY):
    return php_string_encrypt(string, key)


def verify_legacy_password(plain_password: str, hashed_password: str) -> bool:
    # Replicate: md5(encrypted) . sha1(encrypted)
    encrypted_string = php_encrypt(plain_password)
    print(f"DEBUG: php_encrypt output: {encrypted_string}")
    md5_hash = hashlib.md5(encrypted_string.encode()).hexdigest()
    sha1_hash = hashlib.sha1(encrypted_string.encode()).hexdigest()
    final_hash = md5_hash + sha1_hash
    return final_hash == hashed_password

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
