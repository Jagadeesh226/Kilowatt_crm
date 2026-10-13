from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import recommendations as rec_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/generate")
def generate(customer_id: int = Query(...), current_date: str | None = Query(None), db: Session = Depends(get_db)):
    bundle = rec_service.build_recommendation(db, customer_id, current_date)
    if bundle is None:
        raise HTTPException(404, "Customer not found")
    return bundle
