from datetime import datetime
from pydantic import BaseModel

class CheckStudentParms(BaseModel):
    badge_number: int
    post_flag: bool = False

class NewPromotionRecord(BaseModel):
    badge_number: int
    belt_id : int
    belt_name : str
    stripe_id : int
    stripe_name : str
    promotion_date: datetime
    comments : str = ''
    post_flag: bool = False
