from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import CampaignCalendar
from ..schemas import CampaignOut

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    camps = db.query(CampaignCalendar).order_by(CampaignCalendar.start_date).all()
    return [CampaignOut.model_validate(c) for c in camps]

@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    c = db.get(CampaignCalendar, campaign_id)
    if not c:
        raise HTTPException(404, "Campaign not found")
    return CampaignOut.model_validate(c)
