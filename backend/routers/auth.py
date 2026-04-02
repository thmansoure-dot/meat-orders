from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os

from database import get_db
import models, schemas

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "meat-orders-secret-key-change-in-production-2024")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24 * 7  # 1 week

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.id == user_id, models.User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def ensure_default_admin(db: Session):
    """Create default admin user if no users exist."""
    if db.query(models.User).count() == 0:
        admin = models.User(
            username="admin",
            hashed_pw=hash_password("admin123"),
            display_name="المدير"
        )
        db.add(admin)
        db.commit()

@router.post("/login", response_model=schemas.TokenResponse)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    ensure_default_admin(db)
    user = db.query(models.User).filter(
        models.User.username == req.username,
        models.User.is_active == True
    ).first()
    if not user or not verify_password(req.password, user.hashed_pw):
        raise HTTPException(status_code=401, detail="اسم المستخدم أو كلمة المرور خاطئة")
    return schemas.TokenResponse(
        access_token=create_token(user.id),
        display_name=user.display_name or user.username,
        user_id=user.id
    )

@router.get("/me", response_model=schemas.UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[schemas.UserOut])
def list_users(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.post("/users", response_model=schemas.UserOut)
def create_user(req: schemas.UserCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == req.username).first():
        raise HTTPException(status_code=400, detail="اسم المستخدم موجود مسبقاً")
    user = models.User(
        username=req.username,
        hashed_pw=hash_password(req.password),
        display_name=req.display_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="لا يمكن حذف حسابك الحالي")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    db.delete(user)
    db.commit()
    return {"ok": True}

@router.post("/change-password")
def change_password(
    data: dict,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.get("old_password", ""), current_user.hashed_pw):
        raise HTTPException(status_code=400, detail="كلمة المرور الحالية خاطئة")
    current_user.hashed_pw = hash_password(data["new_password"])
    db.commit()
    return {"ok": True}
