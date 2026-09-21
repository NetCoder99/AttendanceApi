# ---------------------------------------------------------------------------------------------------------------------
# sqlacodegen sqlite:///C:\Users\jdugger01\AppData\Roaming\Attendance\AttendanceV3.db --tables archive
# ---------------------------------------------------------------------------------------------------------------------

# import json
# import logging
import logging.config

from sqlalchemy import select

import loggingConf

from fastapi import FastAPI

from models.data_models import Requirements
from models.input_models import CheckStudentParms, NewPromotionRecord, SearchStudentParams
from services.class_procs import GetCurrentClass, GetNextClass
from services.promotions_create import InsNewPromotionRecord
from services.promotions_procs import GetNextStudentRank, GetCrntStudentRank
from services.promotions_update import UpdateStudentRank
from services.sqlite_alchemy import getAlchemySession
from services.student_procs import DelStudentRecord, GetStudentRecord, SearchForStudents
from datetime import datetime

logging_config_dict = loggingConf.LOGGING_CONFIG
logging.config.dictConfig(logging_config_dict)
logger = logging.getLogger(__name__)

app = FastAPI()

db_session = getAlchemySession()

@app.get("/")
def index():
    return {"message": "Welcome to FastAPI"}

# --------------------------------------------------------------------
# Student related end points
# --------------------------------------------------------------------
@app.post("/students/search_for_students/")
def search_for_students(search_student_params: SearchStudentParams):
    try:
        student_records     = SearchForStudents(search_student_params)
        if not search_student_params.include_photo:
            excluded_columns    = ['studentImageBase64','studentImageBytes']
        else:
            excluded_columns    = ['studentImageBytes']
        serialized_students = [
            {col.name: getattr(student, col.name) for col in student.__table__.columns if col.name not in excluded_columns}
            for student in student_records
        ]
        if not student_records:
            return {"status" : "error", "message" : "No student records found", "data" : search_student_params}
        else:
            return {"status": "ok", "message": "get_student_record", "data": serialized_students}
    except Exception as ex:
        logger.exception(f'Error: {str(ex)}')
        return {"status": "error", "message": {str(ex)}, "data": None}

@app.post("/students/get_student_photo/")
def get_student_photo(search_student_params: SearchStudentParams):
    try:
        student_records    = SearchForStudents(search_student_params)
        include_columns    = ['badgeNumber', 'firstName', 'lastName', 'studentImageBase64']
        serialized_students = [
            {col.name: getattr(student, col.name) for col in student.__table__.columns if col.name in include_columns}
            for student in student_records
        ]
        if not student_records:
            return {"status" : "error", "message" : "No student records found", "data" : search_student_params}
        else:
            return {"status": "ok", "message": "get_student_record", "data": serialized_students}
    except Exception as ex:
        logger.exception(f'Error: {str(ex)}')
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

# --------------------------------------------------------------------
# Promotion related end points
# --------------------------------------------------------------------
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

@app.post("/promotions/insert_promotion_record/")
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

@app.post("/promotions/get_all_requirements/")
def get_all_requirements():
    try:
        requirements_records = db_session.scalars(select(Requirements)).all()
        if not requirements_records:
            return {"status" : "error", "message" : "No requirements records were found", "data" : None}
        else:
            return {"status": "ok", "message": "Requirements records", "data": requirements_records}
    except Exception as ex:
        return {"status": "error", "message": {str(ex)}, "data": None}

# --------------------------------------------------------------------
# Promotion related end points
# --------------------------------------------------------------------
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
