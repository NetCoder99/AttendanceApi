import json
import logging.config

from sqlalchemy import select, delete
from sqlalchemy.orm import defer, load_only

from models.data_models import Students, Attendance, Archive, Promotions
from models.input_models import SearchStudentParams
from services.sqlite_alchemy import getAlchemySession

logger = logging.getLogger(__name__)
db_session = getAlchemySession()

# -----------------------------------------------------------------------------------
# commonly used function to get the student record
# -----------------------------------------------------------------------------------
def GetStudentRecord(badge_number: int) -> Students:
    try:
        db_session.expire_all()
        student_list_stmt = select(Students).where(Students.badgeNumber == badge_number)
        return db_session.scalars(student_list_stmt).first()
    except Exception as ex:
        logger.exception(f'Error: {str(ex)}')
        raise ex

def SearchForStudents(search_student_params: SearchStudentParams) -> list[Students]:
    try:
        db_session.expire_all()
        filters = []
        if search_student_params.badge_number != 0:
            filters.append(Students.badgeNumber == search_student_params.badge_number)
        else:
            if search_student_params.first_name != 'string':
                filters.append(Students.firstName.ilike(f"%{search_student_params.first_name}%"))
            if search_student_params.last_name != 'string':
                filters.append(Students.lastName.ilike(f"%{search_student_params.last_name}%"))
        select_stmt = (select(Students).where(*filters))

        logger.info(f'student search select: {str(select_stmt)}')
        student_records = db_session.scalars(select_stmt).all()
        return student_records

    except Exception as ex:
        db_session.rollback()
        logger.exception(f'Error: {str(ex)}')
        raise ex

# def SearchForStudents(search_student_params: SearchStudentParams) -> list[Students]:
#     try:
#         # db_session.expire_all()
#         # query_columns = [c for c in Students.__table__.columns if c.name not in ['studentImageBase64', 'studentImageBytes']]
#         # stmt1          = select(*query_columns).where(Students.badgeNumber == search_student_params.badge_number)
#         # results1       = db_session.scalars(stmt1).all()
#         #
#         # stmt2          = (select(Students)
#         #                   .where(Students.badgeNumber == search_student_params.badge_number)
#         #                   .options(load_only(*query_columns))
#         #                   )
#         # results2       = db_session.scalars(stmt2).all()
#         #
#         #
#         # excluded_cols = [Students.studentImageBase64, Students.studentImageBytes]
#
#
#         if (search_student_params.badge_number == 0
#             and search_student_params.first_name == 'string'
#             and search_student_params.last_name == 'string'
#         ):
#             raise Exception('No valid search parameters were found.')
#
#         if not search_student_params.include_photo:
#             columns_to_defer = [Students.studentImageBase64, Students.studentImageBytes]
#         else:
#             columns_to_defer = []
#
#         if search_student_params.badge_number != 0:
#             select_stmt = (select(Students)
#                            .where(Students.badgeNumber == search_student_params.badge_number)
#                            .options(*(defer(col) for col in columns_to_defer))
#                            )
#             student_records = db_session.scalars(select_stmt).all()
#             return student_records
#
#         filters = []
#         if search_student_params.first_name != 'string':
#             filters.append(Students.firstName.ilike(f"%{search_student_params.first_name}%"))
#         if search_student_params.last_name != 'string':
#             filters.append(Students.lastName.ilike(f"%{search_student_params.last_name}%"))
#
#
#         if search_student_params.include_photo:
#             select_stmt2 = (select(Students).where(*filters))
#         else:
#             select_stmt2 = (select(Students)
#                            .where(*filters)
#                            .options(*(defer(col) for col in columns_to_defer))
#                            )
#         logger.info(f'student search select: {str(select_stmt2)}')
#         student_records = db_session.scalars(select_stmt2).all()
#         return student_records
#
#     except Exception as ex:
#         db_session.rollback()
#         logger.exception(f'Error: {str(ex)}')
#         raise ex

def DelStudentRecord(student_record: Students) -> list[dict]:
    try:
        rtn_list = [
            DelAllAttendanceRecords(student_record),
            DelAllPromotionRecords(student_record)
        ]

        archive_json   = student_record.to_dict()
        archive_record = Archive.fromDict(
            {
                'badgeNumber': student_record.badgeNumber,
                'tableName'  : student_record.__tablename__,
                'archiveJson': json.dumps(archive_json)
            }
        )
        logger.info(f'archive_json: {archive_json}')
        db_session.add(archive_record)
        db_session.delete(student_record)
        db_session.commit()
        rtn_list.append({'tableName': 'Students', 'rowsDeleted': 1})
        return rtn_list
    except Exception as ex:
        db_session.rollback()
        logger.exception(f'Error: {str(ex)}')
        raise ex

def DelAllAttendanceRecords(student_record: Students) -> dict:
    try:
        # save the records to an archive table
        attendance_records = db_session.scalars(
            select(Attendance).where(Attendance.badgeNumber == student_record.badgeNumber)
        ).all()
        for attendance_record in attendance_records:
            archive_json = attendance_record.to_dict()
            archive_record = Archive.fromDict(
                {
                    'badgeNumber' : student_record.badgeNumber,
                    'tableName'   : attendance_record.__tablename__,
                    'archiveJson' : json.dumps(archive_json)
                }
            )
            db_session.add(archive_record)
            logger.info(f'archive_json: {archive_json}')
        db_session.commit()
        # now delete the attendance records
        attendance_del_stmt    = delete(Attendance).where(Attendance.badgeNumber == student_record.badgeNumber)
        attendance_del_result  = db_session.execute(attendance_del_stmt)
        attendance_del_count   = attendance_del_result.rowcount
        db_session.commit()
        return {'tableName': 'Attendance', 'rowsDeleted' : attendance_del_count}
    except Exception as ex:
        db_session.rollback()
        logger.exception(f'Error: {str(ex)}')
        raise ex

# def DelAllAttendanceRecords(student_record: Students) -> dict:
#     try:
#         # save the records to an archive table
#         attendance_records = db_session.scalars(
#             select(Attendance).where(Attendance.badgeNumber == student_record.badgeNumber)
#         ).all()
#         for attendance_record in attendance_records:
#             archive_json = attendance_record.to_dict()
#             archive_record = Archive.fromDict(
#                 {
#                     'badgeNumber' : student_record.badgeNumber,
#                     'tableName'   : attendance_record.__tablename__,
#                     'archiveJson' : json.dumps(archive_json)
#                 }
#             )
#             db_session.add(archive_record)
#             print(f'archive_json: {archive_json}')
#         db_session.commit()
#         # now delete the attendance records
#         attendance_del_stmt    = delete(Attendance).where(Attendance.badgeNumber == student_record.badgeNumber)
#         attendance_del_result  = db_session.execute(attendance_del_stmt)
#         attendance_del_count   = attendance_del_result.rowcount
#         db_session.commit()
#         return {'tableName': 'Attendance', 'rowsDeleted' : attendance_del_count}
#     except Exception as ex:
#         db_session.rollback()
#         print(f'Error: {str(ex)}')
#         raise ex

def DelAllPromotionRecords(student_record: Students) -> dict:
    try:
        # save the records to an archive table
        promotion_records = db_session.scalars(
            select(Promotions).where(Promotions.badgeNumber == student_record.badgeNumber)
        ).all()
        for promotion_record in promotion_records:
            archive_json = promotion_record.to_dict()
            archive_record = Archive.fromDict(
                {
                    'badgeNumber' : student_record.badgeNumber,
                    'tableName'   : promotion_record.__tablename__,
                    'archiveJson' : json.dumps(archive_json)
                }
            )
            db_session.add(archive_record)
            logger.info(f'archive_json: {archive_json}')
        db_session.commit()
        # now delete the promotion records
        promotion_del_stmt    = delete(Promotions).where(Promotions.badgeNumber == student_record.badgeNumber)
        promotion_del_result  = db_session.execute(promotion_del_stmt)
        promotion_del_count   = promotion_del_result.rowcount
        db_session.commit()
        return {'tableName': 'Promotions', 'rowsDeleted' : promotion_del_count}
    except Exception as ex:
        db_session.rollback()
        logger.exception(f'Error: {str(ex)}')
        raise ex
