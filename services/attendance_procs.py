from sqlalchemy import select, func

from models.data_models import Attendance, Promotions
from models.output_models import AttendanceCounts
from services.sqlite_alchemy import getAlchemySession

db_session = getAlchemySession()

def GetAllAttendanceCounts(badge_number: int, last_promotion_record: Promotions | None) -> AttendanceCounts:
    try:
        # instantiate return object
        attendance_counts = AttendanceCounts.construct()

        # begin accumulating counts
        attendance_total_stmt = (select(func.count())
                                 .select_from(Attendance)
                                 .where(Attendance.badgeNumber == badge_number))
        attendance_counts.attendance_count_total = db_session.scalar(attendance_total_stmt)

        # attendance since last belt or stripe requires a promotion record
        if not last_promotion_record:
            attendance_counts.attendance_count_since_belt = -1
            attendance_counts.attendance_count_since_stripe = -1
        else:
            attendance_since_belt_stmt = (select(func.count())
                                          .select_from(Attendance)
                                          .where(Attendance.badgeNumber == badge_number)
                                          .where(Attendance.checkinDateTime >= last_promotion_record.promotionDate)
                                          )
            attendance_counts.attendance_count_since_belt = db_session.scalar(attendance_since_belt_stmt)
            attendance_since_stripe_stmt = (select(func.count())
                                            .select_from(Attendance)
                                            .where(Attendance.badgeNumber == badge_number)
                                            .where(Attendance.checkinDateTime >= last_promotion_record.promotionDate)
                                            )
            attendance_counts.attendance_count_since_stripe = db_session.scalar(attendance_since_stripe_stmt)

        return attendance_counts

    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

