import json
from ..config import OPENAI_API_KEY, OPENAI_MODEL

# Free OpenAI-compatible provider (Groq). Set as a constant so no base URL config is needed.
DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"

SYSTEM_PROMPT = """You are an assistant for a WooCommerce CRM. You must only use facts provided in the evidence bundle.
Do not invent discounts, stock, product features, purchase history, campaign dates, prices, or availability claims.
If evidence is insufficient, state that clearly and suggest no confident recommendation.
Return ONLY valid JSON with keys:
  explanation (string)
  message_draft (string)
  suggested_subject (string or null)
  confidence_note (string)
"""

def generate_explanation(evidence_bundle):
    if not OPENAI_API_KEY:
        return fallback_explanation(evidence_bundle), "fallback"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=DEFAULT_BASE_URL)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(evidence_bundle, default=str)},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
        for key in ("explanation", "message_draft"):
            if key not in data:
                raise ValueError("missing key " + key)
        data.setdefault("suggested_subject", None)
        data.setdefault("confidence_note", "")
        return data, "llm"
    except Exception as e:
        fb = fallback_explanation(evidence_bundle)
        fb["error"] = str(e)
        return fb, "fallback"

def fallback_explanation(bundle):
    customer = bundle.get("customer", {})
    name = customer.get("name", "Customer")
    campaign = bundle.get("selected_campaign")
    reasons = bundle.get("reasons", [])
    if bundle.get("suppressed"):
        explanation = "No outreach recommended: " + "; ".join(bundle.get("suppression_reasons", ["suppressed"]))
        msg = f"Hi {name},\n\nNo personalized outreach is recommended at this time."
    elif bundle.get("candidate_category") and campaign:
        purchase_reason = next((r for r in reasons if r.startswith("Recommended because")), "")
        campaign_reason = next((r for r in reasons if r.startswith("Campaign window open")), "")
        explanation = " ".join([purchase_reason, campaign_reason]).strip() or "Recommendation available."
        msg = (
            f"Hi {name},\n\n"
            f"Based on your previous interest in {bundle['candidate_category']}, and with our {campaign['name']} "
            f"campaign now open, we thought this would be a good time to share relevant options."
        )
    else:
        explanation = "Insufficient evidence for a confident personalized recommendation. " + "; ".join(reasons)
        msg = f"Hi {name},\n\nThank you for being a valued customer."
    return {
        "explanation": explanation,
        "message_draft": msg,
        "suggested_subject": f"{campaign['name']} picks for you" if campaign else "A quick note",
        "confidence_note": bundle.get("confidence", ""),
    }