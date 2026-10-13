from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db, Base, engine

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/demo/reset")
def reset_demo(db: Session = Depends(get_db)):
    # Re-run seed by importing seed module
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app import seed
    seed.run_seed(reset=True)
    return {"status": "ok", "message": "Demo data reset."}

@router.get("/health")
def health():
    return {"status": "ok"}
