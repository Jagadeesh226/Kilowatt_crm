from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from .database import SessionLocal, Base, engine
from .models import Customer, Order, OrderItem, CampaignCalendar, Communication
from .config import reference_date

BASE_DATE = None

def _ref():
    global BASE_DATE
    if BASE_DATE is None:
        BASE_DATE = reference_date()
    return BASE_DATE

def _dt(days_ago=0, hour=10):
    d = _ref() - timedelta(days=days_ago)
    return datetime(d.year, d.month, d.day, hour, 0, 0)

def clear_db(db):
    db.query(Communication).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Customer).delete()
    db.query(CampaignCalendar).delete()
    db.commit()

def add_order(db, customer, days_ago, status, items, hour=11):
    o = Order(
        wc_order_id=None,
        customer_id=customer.id,
        status=status,
        total=sum(qty * price for _, _, qty, price in items),
        currency="INR",
        ordered_at=_dt(days_ago, hour),
    )
    db.add(o)
    db.flush()
    for name, cat, qty, price in items:
        db.add(OrderItem(order_id=o.id, product_name=name, category=cat, quantity=qty, unit_price=price))
    db.commit()
    db.refresh(o)
    return o

def run_seed(reset=True):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if reset:
            clear_db(db)

        ref = _ref()

        # Customers
        customers_data = [
            ("Priya Sharma", "priya@example.com", "+919876543210", "India", True),
            ("Anita Desai", "anita@example.com", "+919876543211", "India", True),
            ("Rohan Mehta", "rohan@example.com", "+919876543212", "India", True),
            ("Sneha Iyer", "sneha@example.com", "+919876543213", "India", True),
            ("Vikram Singh", "vikram@example.com", "+919876543214", "India", True),
            ("Kavita Nair", "kavita@example.com", "+919876543215", "India", False),
            ("Arjun Patel", "arjun@example.com", "+919876543216", "India", True),
            ("Meera Reddy", "meera@example.com", "+919876543217", "India", True),
            ("Sanjay Gupta", "sanjay@example.com", "+919876543218", "India", True),
            ("Divya Joshi", "divya@example.com", "+919876543219", "India", True),
            ("Ramesh Kumar", "ramesh@example.com", "+919876543220", "India", True),
            ("Pooja Verma", "pooja@example.com", "+919876543221", "India", True),
            ("Guest Shopper", None, "+919876543299", "India", True),
        ]
        customers = []
        for i, (name, email, phone, region, consent) in enumerate(customers_data, start=1):
            wc_id = 1000 + i if i < len(customers_data) else None
            c = Customer(
                wc_customer_id=wc_id if i < 12 else None,
                name=name,
                email=email,
                phone=phone,
                region=region,
                marketing_consent=consent,
                created_at=_dt(180 - i * 5, 9),
            )
            db.add(c)
            db.commit()
            db.refresh(c)
            customers.append(c)

        # Campaigns
        campaigns = [
            ("Navaratri Festive Wear", ref - timedelta(days=14) if False else date(2026,10,18), date(2026,10,30), 14, ["ethnic wear", "festive clothing", "jewelry", "puja items"], "India", "Festive apparel and puja essentials for Navaratri."),
            ("Diwali Home & Gifting", date(2026,11,1), date(2026,11,10), 25, ["home decor", "gifts", "sweets", "puja items"], "India", "Diwali gifting and home decor."),
            ("Summer Clearance", date(2026,6,1), date(2026,6,30), 10, ["casual wear"], "India", "Expired summer campaign for testing window logic."),
        ]
        for name, start, end, lead, cats, region, notes in campaigns:
            db.add(CampaignCalendar(name=name, start_date=start, end_date=end, lead_days=lead, eligible_categories=cats, region=region, notes=notes))
        db.commit()

        c = customers
        # P0 Priya: ethnic wear buyer recently -> Navaratri
        add_order(db, c[0], 20, "completed", [("Silk Saree", "ethnic wear", 1, 4500), ("Bangles", "jewelry", 1, 800)])
        add_order(db, c[0], 120, "completed", [("Kurta Set", "ethnic wear", 2, 2200)])
        add_order(db, c[0], 200, "completed", [("Casual Top", "casual wear", 1, 900)])

        # Anita: festive clothing buyer, at-risk
        add_order(db, c[1], 100, "completed", [("Lehenga", "festive clothing", 1, 7800)])
        add_order(db, c[1], 150, "completed", [("Dupatta", "festive clothing", 1, 1200)])
        add_order(db, c[1], 40, "cancelled", [("Heels", "footwear", 1, 1500)])

        # Rohan: recent casual, inactive-ish? 
        add_order(db, c[2], 5, "completed", [("T-Shirt", "casual wear", 2, 700)])
        add_order(db, c[2], 60, "completed", [("Jeans", "casual wear", 1, 1800)])

        # Sneha: high-value jewelry + ethnic
        add_order(db, c[3], 15, "completed", [("Gold Necklace", "jewelry", 1, 18000), ("Earrings", "jewelry", 1, 3500)])
        add_order(db, c[3], 45, "completed", [("Designer Saree", "ethnic wear", 1, 9500)])
        add_order(db, c[3], 10, "refunded", [("Ring", "jewelry", 1, 2000)])

        # Vikram: inactive
        add_order(db, c[4], 260, "completed", [("Puja Thali", "puja items", 1, 1200)])
        add_order(db, c[4], 300, "completed", [("Dhoop", "puja items", 2, 200)])

        # Kavita: no consent, bought ethnic
        add_order(db, c[5], 25, "completed", [("Saree", "ethnic wear", 1, 3000)])

        # Arjun: home decor buyer -> Diwali future
        add_order(db, c[6], 10, "completed", [("Lamp", "home decor", 2, 1500), ("Wall Art", "home decor", 1, 2200)])
        add_order(db, c[6], 90, "processing", [("Cushion", "home decor", 4, 600)])

        # Meera: new customer 10 days ago
        add_order(db, c[7], 10, "completed", [("Kurti", "ethnic wear", 1, 1800)])

        # Sanjay: at-risk ethnic 120 days
        add_order(db, c[8], 120, "completed", [("Sherwani", "festive clothing", 1, 6500)])
        add_order(db, c[8], 200, "completed", [("Stole", "accessories", 1, 900)])

        # Divya: repeat, bought gifts
        add_order(db, c[9], 30, "completed", [("Gift Hamper", "gifts", 3, 1200)])
        add_order(db, c[9], 70, "completed", [("Sweet Box", "sweets", 2, 600)])

        # Ramesh: guest orders only (no registered? customer_id null) handle separately
        guest_order = Order(wc_order_id=9991, customer_id=None, status="completed", total=2500, currency="INR", ordered_at=_dt(12, 10))
        db.add(guest_order)
        db.flush()
        db.add(OrderItem(order_id=guest_order.id, product_name="Puja Kit", category="puja items", quantity=1, unit_price=2500))
        db.commit()

        # assign wc_order_ids
        for o in db.query(Order).all():
            if o.wc_order_id is None:
                o.wc_order_id = 5000 + o.id
        db.commit()

        # guest customer record c[12] use as guest profile? add order linked
        add_order(db, c[12], 25, "completed", [("Incense", "puja items", 2, 300)])

        print("Seed complete")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed(reset=True)
