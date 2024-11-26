from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prisma import Prisma
import jwt
from datetime import datetime, timedelta
import os

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("JWT_SECRET"), algorithm="HS256")
    return encoded_jwt

async def verify_token(credentials: HTTPAuthorizationCredentials = security):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin(request: Request):
    try:
        auth = await verify_token(await security(request))
        if not auth.get("is_admin"):
            raise HTTPException(status_code=403, detail="Not an admin")
        return auth
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_prisma():
    prisma = Prisma()
    await prisma.connect()
    try:
        yield prisma
    finally:
        await prisma.disconnect()
