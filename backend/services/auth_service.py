import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load .env
root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)
else:
    load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mindsync_super_secret_jwt_key_2026_change_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# HTTP Bearer scheme
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = secrets.token_hex(16)
    iterations = 100_000
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    )
    return f"pbkdf2_sha256${iterations}${salt}${hash_bytes.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored PBKDF2 hash."""
    if not hashed_password:
        return False

    # Handle demo hash backwards compatibility
    if hashed_password in ["demo_pass_hash", "pbkdf2_sha256$mockhash$demopassword"]:
        return True

    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = parts[2]
        expected_hex = parts[3]

        calc_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        )
        return secrets.compare_digest(calc_bytes.hex(), expected_hex)
    except Exception as e:
        print(f"[Auth] Error verifying password: {e}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT token with claims and expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to extract and verify the current authenticated user from MongoDB Atlas."""
    from database import get_db, to_object_id

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = get_db()
    oid = to_object_id(user_id)
    query = {"$or": [{"_id": oid}, {"id": user_id}]} if oid else {"id": user_id}
    user = db.users.find_one(query)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with this token not found.",
        )

    user_dict = dict(user)
    oid_val = user.get("_id")
    user_dict["_id"] = oid_val
    user_dict["id"] = str(oid_val) if oid_val else user.get("id")
    user_dict["user_id"] = str(oid_val) if oid_val else user.get("id")
    user_dict.pop("password_hash", None)
    if "created_at" in user_dict and isinstance(user_dict["created_at"], datetime):
        user_dict["created_at"] = user_dict["created_at"].isoformat()
    return user_dict


def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Optional authentication dependency: returns user dict if valid Bearer token provided, or None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return get_current_user(credentials)
    except Exception:
        return None


def get_default_user_oid(db) -> Any:
    """Helper to return an existing user ObjectId for fallback/seeding context."""
    user = db.users.find_one()
    if user and user.get("_id"):
        return user["_id"]
    from bson.objectid import ObjectId
    return ObjectId()
