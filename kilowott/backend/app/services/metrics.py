from datetime import datetime, date, timedelta
from ..config import reference_date

ELIGIBLE_STATUSES = {"completed", "processing"}

def is_eligible(order):
    return (order.status or "").lower() in ELIGIBLE_STATUSES

def _days_since(d, ref=None):
    if d is None:
        return None
    ref = ref or reference_date()
    if isinstance(d, datetime):
        d = d.date()
    return (ref - d).days

def customer_metrics(customer, orders, ref=None):
    ref = ref or reference_date()
    eligible = [o for o in orders if is_eligible(o)]
    eligible_sorted = sorted(eligible, key=lambda o: o.ordered_at, reverse=True)
    lifetime_spend = round(sum(float(o.total or 0) for o in eligible), 2)
    order_count = len(eligible)
    last_order_date = eligible_sorted[0].ordered_at if eligible_sorted else None
    days_since_last = _days_since(last_order_date, ref) if last_order_date else None
    avg_order_value = round(lifetime_spend / order_count, 2) if order_count else 0.0

    cat_qty = {}
    cat_last = {}
    cat_orders = {}
    for o in eligible:
        for item in o.items:
            cat_qty[item.category] = cat_qty.get(item.category, 0) + (item.quantity or 1)
            if item.category not in cat_last or o.ordered_at > cat_last[item.category]:
                cat_last[item.category] = o.ordered_at
            cat_orders.setdefault(item.category, set()).add(o.id)

    top_categories = sorted(cat_qty.items(), key=lambda kv: (-kv[1], kv[0]))
    category_summary = [
        {
            "category": c,
            "quantity": q,
            "last_purchased_at": cat_last[c].isoformat() if isinstance(cat_last[c], datetime) else str(cat_last[c]),
            "order_count": len(cat_orders.get(c, ())),
        }
        for c, q in top_categories
    ]

    repeat_purchase_categories = [c for c, q in top_categories if len(cat_orders.get(c, ())) >= 2]

    return {
        "customer_id": customer.id if customer else None,
        "total_orders": order_count,
        "lifetime_spend": lifetime_spend,
        "average_order_value": avg_order_value,
        "last_order_date": last_order_date.isoformat() if isinstance(last_order_date, datetime) else (str(last_order_date) if last_order_date else None),
        "days_since_last_order": days_since_last,
        "top_categories": category_summary,
        "purchased_categories": list(cat_qty.keys()),
        "category_last_purchase": {k: (v.isoformat() if isinstance(v, datetime) else str(v)) for k, v in cat_last.items()},
        "repeat_purchase_categories": repeat_purchase_categories,
        "all_order_statuses": {s: sum(1 for o in orders if (o.status or "").lower() == s) for s in set((o.status or "").lower() for o in orders)},
    }
