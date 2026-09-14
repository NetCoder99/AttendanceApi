import datetime

from pydantic import BaseModel


class StudentRankFields(BaseModel):
    currentRankNum : int
    currentRankName : str
    currentStripeId : int
    currentStripeName : str
    studentPromotionDate : datetime.datetime
    rankMessage : str


class AttendanceCounts(BaseModel):
    attendance_count_total: int
    attendance_count_since_belt: int
    attendance_count_since_stripe: int



