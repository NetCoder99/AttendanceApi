# --------------------------------------------------------------------
# Search for a class within the start and stop times
# --------------------------------------------------------------------
def GetCurrentClass(day_of_week: int, before_interval:int = 15, after_interval:int = 15):
    #class_times = Classes.objects.filter(class_day_of_week=today).order_by('class_start_time')
    class_times = db_session.query(Classes).filter_by(classDayOfWeek=day_of_week)

    current_date = datetime.now()
    current_date_str = current_date.strftime("%m/%d/%Y")
    date_format = "%m/%d/%Y %I:%M %p"
    for class_record in class_times:
        start_checkin_str  = current_date_str + ' ' + class_record.classStartTime
        start_checkin_date = datetime.strptime(start_checkin_str, date_format)
        finis_checkin_str  = current_date_str + ' ' + class_record.classFinisTime
        finis_checkin_date = datetime.strptime(finis_checkin_str, date_format)

        start_checkin_time = start_checkin_date - timedelta(minutes=before_interval)
        finis_checkin_time = start_checkin_date + timedelta(minutes=after_interval)

        DisplayClassDateTimes(start_checkin_time, finis_checkin_time, current_date)

        if start_checkin_time <= current_date <= finis_checkin_time:
            return class_record

        if start_checkin_date <= current_date <= finis_checkin_date:
            return class_record

    return None