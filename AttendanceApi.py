# ---------------------------------------------------------------------------------------------------------------------
# sqlacodegen sqlite:///C:\Users\jdugger01\AppData\Roaming\Attendance\AttendanceV3.db --tables archive
# ---------------------------------------------------------------------------------------------------------------------

import json
from fastapi import FastAPI

from models.input_models import CheckStudentParms, NewPromotionRecord
from services.promotions_create import InsNewPromotionRecord
from services.promotions_procs import GetStudentRecord, GetNextStudentRank, GetCrntStudentRank
from services.promotions_update import UpdateStudentRank
from services.student_procs import DelStudentRecord
from datetime import datetime

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Welcome to FastAPI"}

@app.post("/students/get_student_record/")
def get_student_record(check_student_params: CheckStudentParms):
    try:
        student_record = GetStudentRecord(check_student_params.badge_number)
        if not student_record:
            return {"status" : "error", "message" : "Student record not found", "data" : None}
        else:
            return {"status": "ok", "message": "get_student_record", "data": student_record}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}

@app.post("/students/get_crnt_rank/")
def get_crnt_rank(check_student_params: CheckStudentParms):
    try:
        student_record = GetStudentRecord(check_student_params.badge_number)
        if not student_record:
            return {"status" : "error", "message" : "Student record not found", "data" : None}
        else:
            next_promotion = GetCrntStudentRank(student_record)
            return {"status": "ok", "message": "next_promotion", "data": next_promotion}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}

@app.post("/students/get_next_rank/")
def get_next_rank(check_student_params: CheckStudentParms):
    try:
        student_record = GetStudentRecord(check_student_params.badge_number)
        if not student_record:
            return {"status" : "error", "message" : "Student record not found", "data" : None}
        else:
            next_promotion = GetNextStudentRank(student_record)
            return {"status": "ok", "message": "next_promotion", "data": next_promotion}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}

@app.post("/students/update_student_rank/")
def insert_promotion_record(promotion_params: NewPromotionRecord):
    try:
        student_record = GetStudentRecord(promotion_params.badge_number)
        if not student_record:
            return {"status" : "error", "message" : "Student record not found", "data" : None}
        else:
            promotion_record = UpdateStudentRank(student_record, promotion_params)
            return {"status": "ok", "message": "New promotion record was inserted", "data": promotion_record}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}

@app.post("/students/insert_promotion_record/")
def insert_promotion_record(promotion_parms: NewPromotionRecord):
    try:
        student_record = GetStudentRecord(promotion_parms.badge_number)
        if not student_record:
            return {"status" : "error", "message" : "Student record not found", "data" : None}
        else:
            promotion_record = InsNewPromotionRecord(student_record, promotion_parms)
            return {"status": "ok", "message": "New promotion record was inserted", "data": promotion_record}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}

@app.post("/students/delete_student_record/")
def delete_student_record(check_student_params: CheckStudentParms):
    try:
        student_record = GetStudentRecord(check_student_params.badge_number)
        if not student_record:
            return {"status" : "error", "message" : "Student record not found", "data" : None}
        else:
            records_deleted = DelStudentRecord(student_record)
            return {"status": "ok", "message": "Student record was archived", "data": records_deleted}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}

@app.post("/classes/get_current_class")
def get_current_class(checkin_datetime: datetime):
    try:
        # class_times = Classes.objects.filter(class_day_of_week=today).order_by('class_start_time')
        class_times = db_session.query(Classes).filter_by(classDayOfWeek=day_of_week)

        current_date = datetime.now()
        current_date_str = current_date.strftime("%m/%d/%Y")
        date_format = "%m/%d/%Y %I:%M %p"
        for class_record in class_times:
            start_checkin_str = current_date_str + ' ' + class_record.classStartTime
            start_checkin_date = datetime.strptime(start_checkin_str, date_format)
            finis_checkin_str = current_date_str + ' ' + class_record.classFinisTime
            finis_checkin_date = datetime.strptime(finis_checkin_str, date_format)

            start_checkin_time = start_checkin_date - timedelta(minutes=before_interval)
            finis_checkin_time = start_checkin_date + timedelta(minutes=after_interval)

            DisplayClassDateTimes(start_checkin_time, finis_checkin_time, current_date)

            if start_checkin_time <= current_date <= finis_checkin_time:
                return class_record

            if start_checkin_date <= current_date <= finis_checkin_date:
                return class_record

        return None

        # student_record = GetStudentRecord(check_student_params.badge_number)
        # if not student_record:
        #     return {"status" : "error", "message" : "Student record not found", "data" : None}
        # else:
        #     records_deleted = DelStudentRecord(student_record)
        #     return {"status": "ok", "message": "Student record was archived", "data": records_deleted}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}
