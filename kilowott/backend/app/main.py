from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import CORS_ORIGINS
from .database import Base, engine
from . import models  # noqa
from .routers import customers, orders, dashboard, calendar, recommendations, communications, sync

app = FastAPI(title="WooCommerce CRM", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (customers, orders, dashboard, calendar, recommendations, communications, sync):
    app.include_router(r.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    db = SessionLocal()
    try:
        from .models import Customer
        if db.query(Customer).count() == 0:
            from . import seed
            seed.run_seed(reset=True)
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}
