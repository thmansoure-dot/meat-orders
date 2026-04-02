from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import engine, Base
from routers import auth, orders, suppliers, products, companies
import models

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="نظام طلبيات الاستيراد", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth.router,      prefix="/api/auth",      tags=["auth"])
app.include_router(orders.router,    prefix="/api/orders",    tags=["orders"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["suppliers"])
app.include_router(products.router,  prefix="/api/products",  tags=["products"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

    @app.get("/")
    def serve_login():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/app")
    def serve_app():
        return FileResponse(os.path.join(frontend_path, "app.html"))

@app.get("/health")
def health():
    return {"status": "ok"}
