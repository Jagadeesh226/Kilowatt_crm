from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Communication, Customer
from ..schemas import CommunicationOut, CommunicationCreate

router = APIRouter(prefix="/communications", tags=["communications"])

@router.get("")
def list_communications(customer_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Communication)
    if customer_id:
        q = q.filter(Communication.customer_id == customer_id)
    items = q.order_by(Communication.created_at.desc()).all()
    return [CommunicationOut.model_validate(c) for c in items]

@router.post("")
def create_communication(payload: CommunicationCreate, db: Session = Depends(get_db)):
    cust = db.get(Customer, payload.customer_id)
    if not cust:
        raise HTTPException(404, "Customer not found")
    comm = Communication(**payload.model_dump())
    db.add(comm)
    db.commit()
    db.refresh(comm)
    return CommunicationOut.model_validate(comm)

@router.patch("/{comm_id}/status")
def update_status(comm_id: int, status: str = Query(...), db: Session = Depends(get_db)):
    comm = db.get(Communication, comm_id)
    if not comm:
        raise HTTPException(404, "Communication not found")
    comm.status = status
    if status in ("approved", "sent"):
        from datetime import datetime
        comm.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(comm)
    return CommunicationOut.model_validate(comm)
