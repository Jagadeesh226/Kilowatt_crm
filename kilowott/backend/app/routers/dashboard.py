from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Customer, Order
from ..services.metrics import customer_metrics, is_eligible
from ..services.segmentation import segment_customer
from ..config import reference_date

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    ref = reference_date()
    customers = db.query(Customer).all()
    orders = db.query(Order).all()
    eligible_orders = [o for o in orders if is_eligible(o)]
    total_revenue = round(sum(float(o.total or 0) for o in eligible_orders), 2)
    segment_counts = {}
    followup_queue = []
    for c in customers:
        cos = [o for o in orders if o.customer_id == c.id]
        m = customer_metrics(c, cos, ref)
        seg, reasons = segment_customer(m)
        segment_counts[seg] = segment_counts.get(seg, 0) + 1
        if seg in ("at-risk", "inactive"):
            followup_queue.append({
                "customer_id": c.id,
                "name": c.name,
                "segment": seg,
                "days_since_last_order": m["days_since_last_order"],
                "lifetime_spend": m["lifetime_spend"],
                "reasons": reasons,
            })
    followup_queue.sort(key=lambda x: (x["segment"] != "inactive", -(x["days_since_last_order"] or 0)))
    # recent orders
    recent_orders = sorted(orders, key=lambda o: o.ordered_at, reverse=True)[:10]
    from ..schemas import OrderOut
    return {
        "reference_date": ref.isoformat(),
        "totals": {
            "customers": len(customers),
            "orders": len(orders),
            "eligible_orders": len(eligible_orders),
            "eligible_revenue": total_revenue,
            "currency": "INR",
        },
        "segment_counts": segment_counts,
        "follow_up_queue": followup_queue[:15],
        "recent_orders": [OrderOut.model_validate(o) for o in recent_orders],
    }
