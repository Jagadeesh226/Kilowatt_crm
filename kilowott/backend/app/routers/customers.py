from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from ..database import get_db
from ..models import Customer, Order, Communication
from ..schemas import CustomerOut
from ..services.metrics import customer_metrics
from ..services.segmentation import segment_customer

router = APIRouter(prefix="/customers", tags=["customers"])

def _customer_orders(db, customer_id):
    return db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.ordered_at.desc()).all()

@router.get("")
def list_customers(
    search: str | None = Query(None),
    segment: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    q = db.query(Customer)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Customer.name.ilike(like), Customer.email.ilike(like), Customer.phone.ilike(like)))
    customers = q.order_by(Customer.id).offset(offset).limit(limit).all()
    result = []
    for c in customers:
        orders = _customer_orders(db, c.id)
        m = customer_metrics(c, orders)
        seg, reasons = segment_customer(m)
        if segment and seg != segment:
            continue
        result.append({
            "customer": CustomerOut.model_validate(c),
            "metrics": m,
            "segment": seg,
            "segment_reasons": reasons,
        })
    return result

@router.get("/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(404, "Customer not found")
    orders = _customer_orders(db, c.id)
    m = customer_metrics(c, orders)
    seg, reasons = segment_customer(m)
    comms = db.query(Communication).filter_by(customer_id=c.id).order_by(Communication.created_at.desc()).all()
    from ..schemas import CommunicationOut
    return {
        "customer": CustomerOut.model_validate(c),
        "metrics": m,
        "segment": seg,
        "segment_reasons": reasons,
        "communications": [CommunicationOut.model_validate(x) for x in comms],
    }

@router.get("/{customer_id}/orders")
def customer_orders(customer_id: int, db: Session = Depends(get_db)):
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(404, "Customer not found")
    orders = _customer_orders(db, customer_id)
    from ..schemas import OrderOut
    return [OrderOut.model_validate(o) for o in orders]

@router.get("/{customer_id}/metrics")
def customer_metrics_endpoint(customer_id: int, db: Session = Depends(get_db)):
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(404, "Customer not found")
    orders = _customer_orders(db, customer_id)
    m = customer_metrics(c, orders)
    seg, reasons = segment_customer(m)
    return {"metrics": m, "segment": seg, "segment_reasons": reasons}
