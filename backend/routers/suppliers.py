from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import get_current_user
import models, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.SupplierOut])
def list_suppliers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    suppliers = db.query(models.Supplier).all()
    return suppliers

@router.post("/", response_model=schemas.SupplierOut)
def create_supplier(sup: schemas.SupplierCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    items_data = sup.items
    sup_dict = sup.dict(exclude={"items"})
    db_sup = models.Supplier(**sup_dict)
    db.add(db_sup)
    db.flush()
    for item in items_data:
        db_item = models.SupplierProduct(supplier_id=db_sup.id, **item.dict())
        db.add(db_item)
    db.commit()
    db.refresh(db_sup)
    return db_sup

@router.put("/{sup_id}", response_model=schemas.SupplierOut)
def update_supplier(sup_id: str, sup: schemas.SupplierUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    db_sup = db.query(models.Supplier).filter(models.Supplier.id == sup_id).first()
    if not db_sup:
        raise HTTPException(404, "المورد غير موجود")
    items_data = sup.items
    for k, v in sup.dict(exclude={"items"}).items():
        setattr(db_sup, k, v)
    # Replace all products
    db.query(models.SupplierProduct).filter(models.SupplierProduct.supplier_id == sup_id).delete()
    for item in items_data:
        db_item = models.SupplierProduct(supplier_id=sup_id, **item.dict())
        db.add(db_item)
    db.commit()
    db.refresh(db_sup)
    return db_sup

@router.delete("/{sup_id}")
def delete_supplier(sup_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    db_sup = db.query(models.Supplier).filter(models.Supplier.id == sup_id).first()
    if not db_sup:
        raise HTTPException(404, "المورد غير موجود")
    db.delete(db_sup)
    db.commit()
    return {"ok": True}
