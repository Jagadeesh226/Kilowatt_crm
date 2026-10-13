from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Any

class CustomerOut(BaseModel):
    id: int
    wc_customer_id: int | None = None
    name: str
    email: str | None = None
    phone: str | None = None
    region: str | None = None
    marketing_consent: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class OrderItemOut(BaseModel):
    id: int
    product_name: str
    category: str
    quantity: int
    unit_price: float
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    wc_order_id: int | None = None
    customer_id: int | None = None
    status: str
    total: float
    currency: str
    ordered_at: datetime
    items: list[OrderItemOut] = []

    class Config:
        from_attributes = True

class CampaignOut(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    lead_days: int
    eligible_categories: list[str] = []
    region: str | None = None
    notes: str | None = None
    class Config:
        from_attributes = True

class CommunicationOut(BaseModel):
    id: int
    customer_id: int
    order_id: int | None = None
    channel: str
    subject: str | None = None
    message: str
    status: str
    recommendation_reason: str | None = None
    created_at: datetime
    approved_at: datetime | None = None
    class Config:
        from_attributes = True

class CommunicationCreate(BaseModel):
    customer_id: int
    order_id: int | None = None
    channel: str = "email"
    subject: str | None = None
    message: str
    recommendation_reason: str | None = None
    status: str = "draft"
