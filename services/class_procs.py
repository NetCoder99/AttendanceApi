# --------------------------------------------------------------------
# Search for a class within the start and stop times
# --------------------------------------------------------------------
import logging
from datetime import date, datetime, timedelta
from typing import Type

import constants
from models.data_models import Classes
from services.sqlite_alchemy import getAlchemySession

# ------------------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
db_session = getAlchemySession()
# ------------------------------------------------------------------------------------------

def GetCurrentClass(checkin_datetime: datetime, before_interval:int = 15, after_interval:int = 15) -> Classes | None:
    try:
        day_of_week = checkin_datetime.date().weekday() + 1
        class_times = db_session.query(Classes).filter_by(classDayOfWeek=day_of_week).order_by(Classes.classCheckinStart)

        checkin_datetime_str = checkin_datetime.strftime("%m/%d/%Y")
        date_format = "%m/%d/%Y %I:%M %p"
        for class_record in class_times:
            start_checkin_str  = checkin_datetime_str + ' ' + class_record.classStartTime
            start_checkin_date = datetime.strptime(start_checkin_str, date_format)
            finis_checkin_str  = checkin_datetime_str + ' ' + class_record.classFinisTime
            # finis_checkin_date = datetime.strptime(finis_checkin_str, date_format)

            start_checkin_time = start_checkin_date - timedelta(minutes=before_interval)
            finis_checkin_time = start_checkin_date + timedelta(minutes=after_interval)

            DisplayClassDateTimes(start_checkin_time, finis_checkin_time, checkin_datetime)

            if start_checkin_time <= checkin_datetime <= finis_checkin_time:
                return class_record

            # if start_checkin_date <= checkin_datetime <= finis_checkin_date:
            #     return class_record

        return None
    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

def GetNextClass(checkin_datetime: datetime, before_interval: int = 15) -> Classes | None:
    try:
        day_of_week = checkin_datetime.date().weekday() + 1
        class_times = db_session.query(Classes).filter_by(classDayOfWeek=day_of_week)
        current_date_str = checkin_datetime.strftime("%m/%d/%Y")
        date_format = "%m/%d/%Y %I:%M %p"
        for class_record in class_times:
            start_checkin_str  = current_date_str + ' ' + class_record.classStartTime
            start_checkin_date = datetime.strptime(start_checkin_str, date_format)
            start_checkin_time = start_checkin_date - timedelta(minutes=before_interval)
            if start_checkin_time >= checkin_datetime:
                return class_record
        return None
    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

# --------------------------------------------------------------------
# Insert the attendance checkin record
# --------------------------------------------------------------------
def DisplayClassDateTimes(start_datetime: date, finis_datetime: date, checkin_date: date = None):
    if checkin_date:
        logger.info(
            f'{checkin_date.strftime(constants.dayNameAbbr)} - '
            f'{start_datetime.strftime(constants.fmtDateTime3)} '
            f'{finis_datetime.strftime(constants.fmtDateTime3)} '
            f'{checkin_date.strftime(constants.fmtDateTime3)}'
        )
    else:
        logger.info(
            f'{checkin_date.strftime(constants.dayNameAbbr)} - '
            f'{start_datetime.strftime(constants.fmtDateTime3)} '
            f'{finis_datetime.strftime(constants.fmtDateTime3)} '
        )
