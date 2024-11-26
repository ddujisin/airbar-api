from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from prisma import Prisma
from datetime import datetime, timedelta
from pydantic import BaseModel
import bcrypt
from ..middleware.auth import get_prisma
from ..middleware.session import SessionManager
from ..config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AdminCreate(BaseModel):
    email: str
    password: str

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    prisma: Prisma = Depends(get_prisma)
):
    admin = await prisma.admin.find_first(
        where={
            "email": form_data.username
        }
    )

    if not admin or not bcrypt.checkpw(form_data.password.encode(), admin.password.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = SessionManager.create_access_token(
        data={"sub": admin.email, "is_admin": True},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    prisma: Prisma = Depends(get_prisma)
):
    try:
        payload = SessionManager.decode_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin = await prisma.admin.find_first(
        where={
            "email": email
        }
    )

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return admin

@router.post("/admin/create")
async def create_admin(
    admin_data: AdminCreate,
    prisma: Prisma = Depends(get_prisma)
):
    # Hash the password
    hashed_password = bcrypt.hashpw(admin_data.password.encode(), bcrypt.gensalt()).decode()

    try:
        admin = await prisma.admin.create(
            data={
                "email": admin_data.email,
                "password": hashed_password
            }
        )
        return {"message": "Admin created successfully", "email": admin.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


