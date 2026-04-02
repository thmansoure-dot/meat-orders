from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# ── Auth ────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    display_name: str
    user_id: str

class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str = ""

class UserOut(BaseModel):
    id: str
    username: str
    display_name: str
    is_active: bool
    class Config: from_attributes = True

# ── Company ─────────────────────────────────────────────
class CompanyBase(BaseModel):
    name: str
    name_en: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    reg: str = ""
    code: str = ""
    notes: str = ""
    logo: str = ""
    color: str = "#1a2235"

class CompanyCreate(CompanyBase): pass
class CompanyUpdate(CompanyBase): pass
class CompanyOut(CompanyBase):
    id: str
    class Config: from_attributes = True

# ── Supplier Product ─────────────────────────────────────
class SupplierProductBase(BaseModel):
    artno: str = ""
    name: str
    type: str = "other"
    price: float = 0.0
    history: List[Any] = []

class SupplierProductOut(SupplierProductBase):
    id: str
    class Config: from_attributes = True

# ── Supplier ─────────────────────────────────────────────
class SupplierBase(BaseModel):
    name: str
    country: str = "ألمانيا"
    address: str = ""
    contact: str = ""
    email: str = ""
    phone: str = ""
    iban: str = ""
    swift: str = ""
    bank: str = ""
    eu_reg: str = ""
    notes: str = ""
    cert_halal: bool = False
    cert_health: bool = False
    cert_iso: bool = False
    cert_brc: bool = False
    cert_organic: bool = False
    last_price_update: str = ""
    items: List[SupplierProductBase] = []

class SupplierCreate(SupplierBase): pass
class SupplierUpdate(SupplierBase): pass
class SupplierOut(SupplierBase):
    id: str
    items: List[SupplierProductOut] = []
    class Config: from_attributes = True

# ── Order Item ───────────────────────────────────────────
class OrderItemBase(BaseModel):
    product_name: str = ""
    meat_type: str = ""
    cartons: float = 0
    carton_weight: float = 20
    qty: float = 0
    price: float = 0
    note: str = ""
    cut: str = ""
    total: float = 0
    sort_order: int = 0

class OrderItemOut(OrderItemBase):
    id: str
    class Config: from_attributes = True

# ── Order ────────────────────────────────────────────────
class OrderBase(BaseModel):
    number: str
    supplier_id: Optional[str] = None
    company_id: Optional[str] = None
    week: Optional[int] = None
    week_year: Optional[int] = None
    date: str = ""
    delivery_date: str = ""
    delivery_place: str = ""
    payment: str = ""
    status: str = "pending"
    total: float = 0.0
    notes: str = ""
    reminder_days: Optional[int] = None
    reminder_note: str = ""
    docs_status: str = "ok"
    docs: List[Any] = []
    issues: List[Any] = []
    confirm_data: Optional[Any] = None
    confirm_date: str = ""
    original_items: Optional[Any] = None
    original_total: Optional[float] = None
    items: List[OrderItemBase] = []

class OrderCreate(OrderBase): pass
class OrderUpdate(OrderBase): pass
class OrderOut(OrderBase):
    id: str
    items: List[OrderItemOut] = []
    class Config: from_attributes = True

# ── Product (global) ─────────────────────────────────────
class ProductBase(BaseModel):
    name: str
    type: str = "chicken"
    supplier_id: Optional[str] = None
    price: float = 0.0
    unit: str = "كغ"
    notes: str = ""

class ProductCreate(ProductBase): pass
class ProductUpdate(ProductBase): pass
class ProductOut(ProductBase):
    id: str
    class Config: from_attributes = True
