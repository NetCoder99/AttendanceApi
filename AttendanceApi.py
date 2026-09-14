# ---------------------------------------------------------------------------------------------------------------------
# sqlacodegen sqlite:///C:\Users\jdugger01\AppData\Roaming\Attendance\AttendanceV3.db --tables archive
# ---------------------------------------------------------------------------------------------------------------------

# import json
# import logging
import logging.config

import loggingConf

from fastapi import FastAPI

from models.input_models import CheckStudentParms, NewPromotionRecord, SearchStudentParams
from services.class_procs import GetCurrentClass, GetNextClass
from services.promotions_create import InsNewPromotionRecord
from services.promotions_procs import GetStudentRecord, GetNextStudentRank, GetCrntStudentRank
from services.promotions_update import UpdateStudentRank
from services.student_procs import DelStudentRecord
from datetime import datetime

logging_config_dict = loggingConf.LOGGING_CONFIG
logging.config.dictConfig(logging_config_dict)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Welcome to FastAPI"}

@app.post("/students/search_for_students/")
def search_for_students(search_student_params: SearchStudentParams):
    try:
        student_record = None  #  GetStudentRecord(check_student_params.badge_number)
        if not student_record:
            return {"status" : "error", "message" : "No student records found", "data" : search_student_params}
        else:
            return {"status": "ok", "message": "get_student_record", "data": student_record}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}

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

@app.post("/students/create_student_record/")
def create_student_record(check_student_params: CheckStudentParms):
    try:
        return {"status": "error", "message": "Student create function not implemented.", "data": None}
        # student_record = GetStudentRecord(check_student_params.badge_number)
        # if not student_record:
        #     return {"status" : "error", "message" : "Student record not found", "data" : None}
        # else:
        #     return {"status": "ok", "message": "get_student_record", "data": student_record}
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
def get_current_class(checkin_datetime: datetime = datetime.now(), before_interval: int = 15, after_interval:int = 15):
    try:
        class_record = GetCurrentClass(checkin_datetime, before_interval, after_interval)
        if not class_record:
            return {"status" : "error", "message" : "Class record not found", "data" : None}
        else:
            return {"status": "ok", "message": "Current class", "data": class_record}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}

@app.post("/classes/get_next_class")
def get_next_class(checkin_datetime: datetime = datetime.now(), before_interval: int = 15):
    try:
        class_record = GetNextClass(checkin_datetime)
        if not class_record:
            return {"status" : "error", "message" : "Class record not found", "data" : None}
        else:
            return {"status": "ok", "message": "Current class", "data": class_record}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}
