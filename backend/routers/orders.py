from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import get_current_user
import models, schemas

router = APIRouter()

def order_to_schema(o: models.Order) -> schemas.OrderOut:
    items = sorted(o.items, key=lambda x: x.sort_order)
    return schemas.OrderOut(
        id=o.id, number=o.number,
        supplier_id=o.supplier_id, company_id=o.company_id,
        week=o.week, week_year=o.week_year,
        date=o.date, delivery_date=o.delivery_date,
        delivery_place=o.delivery_place, payment=o.payment,
        status=o.status, total=o.total, notes=o.notes,
        reminder_days=o.reminder_days, reminder_note=o.reminder_note,
        docs_status=o.docs_status, docs=o.docs or [],
        issues=o.issues or [], confirm_data=o.confirm_data,
        confirm_date=o.confirm_date or "",
        original_items=o.original_items, original_total=o.original_total,
        items=[schemas.OrderItemOut(
            id=i.id, product_name=i.product_name, meat_type=i.meat_type,
            cartons=i.cartons, carton_weight=i.carton_weight,
            qty=i.qty, price=i.price, note=i.note, cut=i.cut,
            total=i.total, sort_order=i.sort_order
        ) for i in items]
    )

@router.get("/", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db), _=Depends(get_current_user)):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return [order_to_schema(o) for o in orders]

@router.post("/", response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    items_data = order.items
    order_dict = order.dict(exclude={"items"})
    db_order = models.Order(**order_dict)
    db.add(db_order)
    db.flush()
    for idx, item in enumerate(items_data):
        db_item = models.OrderItem(order_id=db_order.id, sort_order=idx, **item.dict(exclude={"sort_order"}))
        db.add(db_item)
    db.commit()
    db.refresh(db_order)
    return order_to_schema(db_order)

@router.put("/{order_id}", response_model=schemas.OrderOut)
def update_order(order_id: str, order: schemas.OrderUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(404, "الطلبية غير موجودة")
    items_data = order.items
    for k, v in order.dict(exclude={"items"}).items():
        setattr(db_order, k, v)
    db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).delete()
    for idx, item in enumerate(items_data):
        db_item = models.OrderItem(order_id=order_id, sort_order=idx, **item.dict(exclude={"sort_order"}))
        db.add(db_item)
    db.commit()
    db.refresh(db_order)
    return order_to_schema(db_order)

@router.delete("/{order_id}")
def delete_order(order_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(404, "الطلبية غير موجودة")
    db.delete(db_order)
    db.commit()
    return {"ok": True}
