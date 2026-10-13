from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Order, Customer
from ..schemas import OrderOut
from ..services.metrics import is_eligible

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("")
def list_orders(
    status: str | None = None,
    customer_id: int | None = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    if customer_id:
        q = q.filter(Order.customer_id == customer_id)
    orders = q.order_by(Order.ordered_at.desc()).offset(offset).limit(limit).all()
    return [OrderOut.model_validate(o) for o in orders]

@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    o = db.get(Order, order_id)
    if not o:
        raise HTTPException(404, "Order not found")
    return OrderOut.model_validate(o)
