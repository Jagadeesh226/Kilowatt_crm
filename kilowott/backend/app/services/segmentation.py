HIGH_VALUE_THRESHOLD = 25000.0
NEW_CUSTOMER_DAYS = 30
AT_RISK_MIN_DAYS = 91
AT_RISK_MAX_DAYS = 180

def segment_customer(metrics):
    reasons = []
    orders = metrics["total_orders"]
    days = metrics["days_since_last_order"]
    spend = metrics["lifetime_spend"]

    if orders == 0 or days is None:
        segment = "new"
        reasons.append("No eligible orders recorded yet; treat as new/unproven customer.")
        return segment, reasons

    if orders == 1 and days <= NEW_CUSTOMER_DAYS:
        segment = "new"
        reasons.append(f"First eligible order was {days} day(s) ago.")
        return segment, reasons

    if days > AT_RISK_MAX_DAYS:
        segment = "inactive"
        reasons.append(f"No eligible order for {days} days (over {AT_RISK_MAX_DAYS}).")
        if orders >= 2:
            reasons.append(f"Previously made {orders} eligible orders.")
        return segment, reasons

    if days >= AT_RISK_MIN_DAYS:
        segment = "at-risk"
        reasons.append(f"No eligible order for {days} days; within at-risk window.")
        return segment, reasons

    if spend >= HIGH_VALUE_THRESHOLD and orders >= 2:
        segment = "high-value"
        reasons.append(f"Lifetime eligible spend {spend} reached high-value threshold.")
        reasons.append(f"{orders} eligible orders.")
        return segment, reasons

    if orders >= 2:
        segment = "repeat"
        reasons.append(f"{orders} eligible orders; last order {days} day(s) ago.")
        if metrics.get("repeat_purchase_categories"):
            reasons.append("Repeat categories: " + ", ".join(metrics["repeat_purchase_categories"]) + ".")
        return segment, reasons

    segment = "active"
    reasons.append(f"Active customer with {orders} eligible order(s).")
    return segment, reasons
