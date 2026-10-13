from datetime import date, timedelta, datetime
from ..config import reference_date
from ..models import Customer, Order, CampaignCalendar, Communication
from .metrics import customer_metrics
from .segmentation import segment_customer
from .llm import generate_explanation

SUPPRESSION_RECENT_DAYS = 7
COMPLEMENTS = {
    "casual wear": ["festive clothing", "accessories"],
    "home decor": ["puja items", "gifts"],
    "jewelry": ["ethnic wear"],
}

def _as_date(d):
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    return date.fromisoformat(str(d))

def build_recommendation(db, customer_id, current_date=None):
    ref = _as_date(current_date) if current_date else reference_date()
    customer = db.get(Customer, customer_id)
    if not customer:
        return None

    orders = (
        db.query(Order)
        .filter(Order.customer_id == customer_id)
        .order_by(Order.ordered_at.desc())
        .all()
    )
    # include order items
    for o in orders:
        _ = o.items  # ensure loaded

    m = customer_metrics(customer, orders, ref)
    segment, seg_reasons = segment_customer(m)

    campaigns_all = db.query(CampaignCalendar).all()
    active_campaigns = []
    for c in campaigns_all:
        lead_start = c.start_date - timedelta(days=c.lead_days)
        region_ok = (c.region is None or customer.region is None or c.region == customer.region)
        if lead_start <= ref <= c.end_date and region_ok:
            active_campaigns.append(c)

    purchased = m["purchased_categories"]
    purchased_set = set(purchased)
    cat_last = {k: _as_date(v) if not isinstance(v, date) else v for k, v in {kk: vv for kk, vv in [(x["category"], None) for x in []]}.items()} if False else {}
    # rebuild category last purchase dates properly
    cat_last_dates = {}
    for cs in m["top_categories"]:
        cat = cs["category"]
        # find last purchase date string -> date
        try:
            cat_last_dates[cat] = _as_date(cs["last_purchased_at"]) if cs.get("last_purchased_at") else None
        except Exception:
            cat_last_dates[cat] = None

    reasons = list(seg_reasons)
    reasons.append(f"Active seasonal campaigns considered: {', '.join(c.name for c in active_campaigns) if active_campaigns else 'none'}.")

    # Candidate selection
    candidate_category = None
    selected_campaign = None
    campaign_scores = []
    for camp in active_campaigns:
        elig = set(camp.eligible_categories or [])
        overlap = elig & purchased_set
        # complementary
        comp_hits = []
        for pc in purchased:
            for comp in COMPLEMENTS.get(pc, []):
                if comp in elig:
                    comp_hits.append((pc, comp))
        score = 0
        cand = None
        if overlap:
            # choose most recent + most purchased category among overlap
            def cat_key(c):
                lp = cat_last_dates.get(c) or date.min
                qty = next((x for x in m["top_categories"] if x["category"] == c), {}).get("quantity", 0)
                return (lp, qty)
            cand = max(overlap, key=cat_key)
            score += 3
        elif comp_hits:
            pc, comp = comp_hits[0]
            cand = comp
            reasons.append(f"Complementary suggestion: {comp} related to prior {pc} purchase.")
            score += 1
        if cand:
            campaign_scores.append((score, camp, cand))
    if campaign_scores:
        campaign_scores.sort(key=lambda x: (-x[0], x[1].start_date))
        _, selected_campaign, candidate_category = campaign_scores[0]

    # If high/low etc. Add purchase evidence reason
    if candidate_category and selected_campaign:
        # find example orders with category
        supporting_orders = []
        for o in orders:
            if any(i.category == candidate_category or i.category in ([c for c in [candidate_category]]) for i in o.items):
                supporting_orders.append(o)
            # include overlapping original purchase categories too
        # evidence: orders containing any category that justifies candidate
        relevant_cats = {candidate_category}
        # if complementary, include original purchased cat? We'll just use candidate-related orders; plus any prior purchases in overlapping categories
        # Determine justification categories: if candidate in purchased_set direct; else purchased categories that map
        justifying = [c for c in purchased if c == candidate_category or candidate_category in COMPLEMENTS.get(c, [])]
        if not justifying:
            justifying = [candidate_category]
        evidence_orders = []
        for o in orders:
            if any(i.category in justifying for i in o.items):
                evidence_orders.append(o)
        evidence = []
        for o in evidence_orders[:5]:
            cats = sorted({i.category for i in o.items if i.category in justifying or i.category == candidate_category})
            if not cats:
                cats = sorted({i.category for i in o.items})
            evidence.append({
                "order_id": o.id,
                "wc_order_id": o.wc_order_id,
                "ordered_at": o.ordered_at.date().isoformat() if isinstance(o.ordered_at, datetime) else str(o.ordered_at),
                "status": o.status,
                "total": float(o.total or 0),
                "categories": cats,
            })
        # reasons
        if candidate_category in purchased_set:
            lp = cat_last_dates.get(candidate_category)
            reasons.append(f"Recommended because customer previously purchased {candidate_category}" + (f" (last on {lp.isoformat() if lp else ''})." if lp else "."))
        reasons.append(f"Campaign window open: {selected_campaign.name} ({selected_campaign.start_date.isoformat()} to {selected_campaign.end_date.isoformat()}, lead {selected_campaign.lead_days} days).")
    else:
        evidence = []
        # build recent evidence anyway
        for o in orders[:5]:
            evidence.append({
                "order_id": o.id,
                "wc_order_id": o.wc_order_id,
                "ordered_at": o.ordered_at.date().isoformat() if isinstance(o.ordered_at, datetime) else str(o.ordered_at),
                "status": o.status,
                "total": float(o.total or 0),
                "categories": sorted({i.category for i in o.items}),
            })
        if active_campaigns:
            reasons.append("No purchased category overlaps active campaign eligible categories.")
        else:
            reasons.append("No active seasonal campaign window for this customer.")

    # Suppression reasons & suppressed flag
    suppression_reasons = []
    suppressed = False
    if not customer.marketing_consent:
        suppressed = True
        suppression_reasons.append("Customer has not consented to marketing.")
    if candidate_category and cat_last_dates.get(candidate_category) and (ref - cat_last_dates[candidate_category]).days < SUPPRESSION_RECENT_DAYS:
        suppressed = True
        suppression_reasons.append(f"Recent purchase of {candidate_category} within {SUPPRESSION_RECENT_DAYS} days; suppress outreach.")
    if m["days_since_last_order"] is not None and m["days_since_last_order"] <= 3 and candidate_category is None:
        # very recent order; optional suppress frequent outreach
        pass
    # If no eligible orders
    if m["total_orders"] == 0:
        suppressed = True
        suppression_reasons.append("No eligible purchase history; insufficient evidence.")

    # Reactivation suggestion if at-risk/inactive with no seasonal candidate
    reactivation = None
    if candidate_category is None and segment in ("at-risk", "inactive"):
        reactivation = "re-engagement check-in"
        reasons.append(f"Customer is {segment}; consider a non-promotional re-engagement message.")

    # Confidence
    if suppressed and not candidate_category:
        confidence = "low (insufficient/ suppressed)"
    elif candidate_category and selected_campaign:
        confidence = "high" if (candidate_category in purchased_set) else "medium"
    elif active_campaigns:
        confidence = "medium (seasonal only)"
    else:
        confidence = "low (insufficient evidence)"

    if suppressed and candidate_category:
        # keep candidate but note suppression
        confidence = "low (suppressed)"

    selected_campaign_dict = None
    if selected_campaign:
        selected_campaign_dict = {
            "id": selected_campaign.id,
            "name": selected_campaign.name,
            "start_date": selected_campaign.start_date.isoformat(),
            "end_date": selected_campaign.end_date.isoformat(),
            "lead_days": selected_campaign.lead_days,
            "lead_window_start": (selected_campaign.start_date - timedelta(days=selected_campaign.lead_days)).isoformat(),
            "eligible_categories": selected_campaign.eligible_categories or [],
            "region": selected_campaign.region,
        }

    active_campaign_list = [
        {
            "id": c.id,
            "name": c.name,
            "start_date": c.start_date.isoformat(),
            "end_date": c.end_date.isoformat(),
            "lead_days": c.lead_days,
            "lead_window_start": (c.start_date - timedelta(days=c.lead_days)).isoformat(),
            "eligible_categories": c.eligible_categories or [],
            "region": c.region,
        }
        for c in active_campaigns
    ]

    # timing for selected
    timing = None
    if selected_campaign:
        timing = {
            "campaign_start": selected_campaign.start_date.isoformat(),
            "campaign_end": selected_campaign.end_date.isoformat(),
            "lead_days": selected_campaign.lead_days,
            "lead_window_start": (selected_campaign.start_date - timedelta(days=selected_campaign.lead_days)).isoformat(),
            "evaluation_date": ref.isoformat(),
        }

    bundle = {
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "region": customer.region,
            "segment": segment,
            "marketing_consent": customer.marketing_consent,
        },
        "metrics": {
            "total_orders": m["total_orders"],
            "lifetime_spend": m["lifetime_spend"],
            "days_since_last_order": m["days_since_last_order"],
            "last_order_date": m["last_order_date"],
            "top_categories": m["top_categories"],
        },
        "candidate_category": candidate_category if not suppressed else (candidate_category if candidate_category else None),
        "reactivation": reactivation,
        "selected_campaign": selected_campaign_dict,
        "active_campaigns": active_campaign_list,
        "suppressed": suppressed,
        "suppression_reasons": suppression_reasons,
        "confidence": confidence,
        "reasons": reasons,
        "evidence": evidence,
        "timing": timing,
        "current_date": ref.isoformat(),
    }

    # If suppressed due to consent, remove candidate? Keep for explanation but mark. We'll let candidate remain maybe null if suppressed by no history. For consent suppression, still show candidate? Suppression says avoid outreach; candidate irrelevant. Set candidate None if suppressed.
    if suppressed:
        bundle["candidate_category"] = None
        bundle["reactivation"] = None

    explanation, source = generate_explanation(bundle)
    bundle["ai"] = {"source": source, **explanation}

    # final candidate output: if reactivation, candidate maybe "Customer re-engagement"
    if reactivation and bundle["candidate_category"] is None and not suppressed:
        bundle["candidate_category"] = "Re-engagement (no product category)"

    return bundle
