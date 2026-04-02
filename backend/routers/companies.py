from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import get_current_user
import models, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.CompanyOut])
def list_companies(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Company).all()

@router.post("/", response_model=schemas.CompanyOut)
def create_company(comp: schemas.CompanyCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    db_comp = models.Company(**comp.dict())
    db.add(db_comp)
    db.commit()
    db.refresh(db_comp)
    return db_comp

@router.put("/{comp_id}", response_model=schemas.CompanyOut)
def update_company(comp_id: str, comp: schemas.CompanyUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    db_comp = db.query(models.Company).filter(models.Company.id == comp_id).first()
    if not db_comp:
        raise HTTPException(404, "الشركة غير موجودة")
    for k, v in comp.dict().items():
        setattr(db_comp, k, v)
    db.commit()
    db.refresh(db_comp)
    return db_comp

@router.delete("/{comp_id}")
def delete_company(comp_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    db_comp = db.query(models.Company).filter(models.Company.id == comp_id).first()
    if not db_comp:
        raise HTTPException(404, "الشركة غير موجودة")
    db.delete(db_comp)
    db.commit()
    return {"ok": True}
