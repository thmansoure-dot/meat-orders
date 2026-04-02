from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import get_current_user
import models, schemas

router = APIRouter()

# Re-use SupplierProduct table but filter by supplier_id
@router.get("/", response_model=list[schemas.ProductOut])
def list_products(db: Session = Depends(get_db), _=Depends(get_current_user)):
    # Global products are stored in supplier_products with a special flag
    # For simplicity, return them as-is; frontend handles display
    rows = db.query(models.SupplierProduct).all()
    return [
        schemas.ProductOut(
            id=r.id,
            name=r.name,
            type=r.type,
            supplier_id=r.supplier_id,
            price=r.price,
            unit="كغ",
            notes=""
        )
        for r in rows
    ]
