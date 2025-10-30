import re, pdfplumber
from pydantic import BaseModel
from typing import Optional, List

class CreditTier(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    risk: str
    max_dti: Optional[float] = None
    special_income_min: Optional[int] = None

class Policy(BaseModel):
    credit_tiers: List[CreditTier]
    income_min_annual: int
    employment_min_months: int
    employment_min_months_self_employed: int
    first_time_buyer_dti_add: float

def extract_text(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)