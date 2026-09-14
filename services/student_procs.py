import json

from sqlalchemy import select, delete

from models.data_models import Students, Attendance, Archive, Promotions
from services.sqlite_alchemy import getAlchemySession

db_session = getAlchemySession()

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
        print(f'archive_json: {archive_json}')
        db_session.add(archive_record)
        db_session.delete(student_record)
        db_session.commit()
        rtn_list.append({'tableName': 'Students', 'rowsDeleted': 1})
        return rtn_list
    except Exception as ex:
        db_session.rollback()
        print(f'Error: {str(ex)}')
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
            print(f'archive_json: {archive_json}')
        db_session.commit()
        # now delete the attendance records
        attendance_del_stmt    = delete(Attendance).where(Attendance.badgeNumber == student_record.badgeNumber)
        attendance_del_result  = db_session.execute(attendance_del_stmt)
        attendance_del_count   = attendance_del_result.rowcount
        db_session.commit()
        return {'tableName': 'Attendance', 'rowsDeleted' : attendance_del_count}
    except Exception as ex:
        db_session.rollback()
        print(f'Error: {str(ex)}')
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
            print(f'archive_json: {archive_json}')
        db_session.commit()
        # now delete the promotion records
        promotion_del_stmt    = delete(Promotions).where(Promotions.badgeNumber == student_record.badgeNumber)
        promotion_del_result  = db_session.execute(promotion_del_stmt)
        promotion_del_count   = promotion_del_result.rowcount
        db_session.commit()
        return {'tableName': 'Promotions', 'rowsDeleted' : promotion_del_count}
    except Exception as ex:
        db_session.rollback()
        print(f'Error: {str(ex)}')
        raise ex
