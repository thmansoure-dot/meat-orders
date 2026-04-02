from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

def gen_id():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id           = Column(String, primary_key=True, default=gen_id)
    username     = Column(String, unique=True, nullable=False, index=True)
    hashed_pw    = Column(String, nullable=False)
    display_name = Column(String, default="")
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    is_active    = Column(Boolean, default=True)

class Company(Base):
    __tablename__ = "companies"
    id         = Column(String, primary_key=True, default=gen_id)
    name       = Column(String, nullable=False)
    name_en    = Column(String, default="")
    address    = Column(String, default="")
    phone      = Column(String, default="")
    email      = Column(String, default="")
    reg        = Column(String, default="")
    code       = Column(String, default="")
    notes      = Column(Text, default="")
    logo       = Column(Text, default="")   # base64
    color      = Column(String, default="#1a2235")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    orders     = relationship("Order", back_populates="company")

class Supplier(Base):
    __tablename__ = "suppliers"
    id           = Column(String, primary_key=True, default=gen_id)
    name         = Column(String, nullable=False)
    country      = Column(String, default="ألمانيا")
    address      = Column(String, default="")
    contact      = Column(String, default="")
    email        = Column(String, default="")
    phone        = Column(String, default="")
    iban         = Column(String, default="")
    swift        = Column(String, default="")
    bank         = Column(String, default="")
    eu_reg       = Column(String, default="")
    notes        = Column(Text, default="")
    cert_halal   = Column(Boolean, default=False)
    cert_health  = Column(Boolean, default=False)
    cert_iso     = Column(Boolean, default=False)
    cert_brc     = Column(Boolean, default=False)
    cert_organic = Column(Boolean, default=False)
    last_price_update = Column(String, default="")
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    items        = relationship("SupplierProduct", back_populates="supplier", cascade="all, delete-orphan")
    orders       = relationship("Order", back_populates="supplier")

class SupplierProduct(Base):
    __tablename__ = "supplier_products"
    id          = Column(String, primary_key=True, default=gen_id)
    supplier_id = Column(String, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    artno       = Column(String, default="")
    name        = Column(String, nullable=False)
    type        = Column(String, default="other")   # chicken/beef/lamb/veal/other
    price       = Column(Float, default=0.0)
    history     = Column(JSON, default=list)        # [{week, price, date}]
    supplier    = relationship("Supplier", back_populates="items")

class Order(Base):
    __tablename__ = "orders"
    id              = Column(String, primary_key=True, default=gen_id)
    number          = Column(String, nullable=False)
    supplier_id     = Column(String, ForeignKey("suppliers.id"), nullable=True)
    company_id      = Column(String, ForeignKey("companies.id"), nullable=True)
    week            = Column(Integer, nullable=True)
    week_year       = Column(Integer, nullable=True)
    date            = Column(String, default="")
    delivery_date   = Column(String, default="")
    delivery_place  = Column(String, default="")
    payment         = Column(String, default="")
    status          = Column(String, default="pending")  # pending/sent/received/cancelled
    total           = Column(Float, default=0.0)
    notes           = Column(Text, default="")
    reminder_days   = Column(Integer, nullable=True)
    reminder_note   = Column(String, default="")
    docs_status     = Column(String, default="ok")
    docs            = Column(JSON, default=list)
    issues          = Column(JSON, default=list)
    confirm_data    = Column(JSON, nullable=True)
    confirm_date    = Column(String, default="")
    original_items  = Column(JSON, nullable=True)
    original_total  = Column(Float, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    supplier        = relationship("Supplier", back_populates="orders")
    company         = relationship("Company", back_populates="orders")
    items           = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id            = Column(String, primary_key=True, default=gen_id)
    order_id      = Column(String, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_name  = Column(String, default="")
    meat_type     = Column(String, default="")
    cartons       = Column(Float, default=0)
    carton_weight = Column(Float, default=20)
    qty           = Column(Float, default=0)
    price         = Column(Float, default=0)
    note          = Column(String, default="")
    cut           = Column(String, default="")
    total         = Column(Float, default=0)
    sort_order    = Column(Integer, default=0)
    order         = relationship("Order", back_populates="items")
