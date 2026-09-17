import constants
from sqlalchemy import select, func
from datetime import datetime
from models.data_models import Students, Promotions, Attendance, Requirements
from models.output_models import StudentRankFields
from services.sqlite_alchemy import getAlchemySession

db_session = getAlchemySession()

# -----------------------------------------------------------------------------------
# commonly used function to get the student record
# -----------------------------------------------------------------------------------
def GetStudentRecord(badge_number: int) -> Students:
    db_session.expire_all()
    student_list_stmt = select(Students).where(Students.badgeNumber == badge_number)
    return db_session.scalars(student_list_stmt).first()

# -----------------------------------------------------------------------------------
# during development the student rank/stripe is not reliably set, thus a complex
# set of calculations to determine the next available belt and/or stripe
# -----------------------------------------------------------------------------------
def GetCrntStudentRank(student_record: Students) -> StudentRankFields:
    try:
        # if rank and stripe are set on the student record then return that
        if student_record.currentRankNum and student_record.currentStripeId:
            student_rank = StudentRankFields.construct()
            student_rank.currentRankNum     = student_record.currentRankNum
            student_rank.currentRankName    = student_record.currentRankName
            student_rank.currentStripeId    = student_record.currentStripeId
            student_rank.currentStripeName  = student_record.currentStripeName
            student_rank.studentPromotionDate = student_record.studentPromotionDate
            student_rank.rankMessage = "From student record"
            return student_rank

        # if both rank and stripe are 'None' then check for a promotion record, use that if found
        last_promotion_record = GetLastPromotionRecord(student_record.badgeNumber)
        if last_promotion_record:
            next_student_rank = GetNextFromLastPromotion(last_promotion_record)
            return next_student_rank

        # not set on student record and no promotion history, use total classes attended
        next_student_rank = GetBasedOnAttendanceTotalCount(student_record)
        return next_student_rank

    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

# -----------------------------------------------------------------------------------
# during development the student rank/stripe is not reliably set, thus a complex
# set of calculations to determine the next available belt and/or stripe
# -----------------------------------------------------------------------------------
def GetNextStudentRank(student_record: Students) -> StudentRankFields:
    try:
        # if rank and stripe are set on the student record then find the next
        # promotion / requirement type
        if student_record.currentRankNum and student_record.currentStripeId:
            next_student_rank = GetNextFromCurrent(student_record)
            return next_student_rank

        # if both rank and stripe are 'None' then check for a promotion record, use that if found
        last_promotion_record = GetLastPromotionRecord(student_record.badgeNumber)
        if last_promotion_record:
            next_student_rank = GetNextFromLastPromotion(last_promotion_record)
            return next_student_rank

        # not set on student record and no promotion history, use total classes attended
        next_student_rank = GetBasedOnAttendanceTotalCount(student_record)
        return next_student_rank

        # # this is rare, but I wanted to deal with it, there is a stripe id but no belt id,
        # # then set the belt id/name
        # elif not student_record.currentRankNum and student_record.currentStripeId:
        #     next_student_rank = GetBasedOnAttendanceTotalCount(student_record)
        #
        # else:
        #     next_student_rank = GetBasedOnAttendanceTotalCount(student_record)

        # # this is rare, but I wanted to deal with it, there is a stripe id but no belt id
        # elif not student_record.currentRankNum and student_record.currentStripeId:
        #     next_student_rank = GetNextFromStripe(student_record)
        #
        #     requirement_record_stmt = (
        #         select(Requirements)
        #         .where(Requirements.stripeId == student_record.currentStripeId)
        #     )
        #     requirement_record = db_session.scalars(requirement_record_stmt).first()
        #     next_student_rank.currentRankNum = requirement_record.beltId
        #     next_student_rank.currentRankName = requirement_record.beltTitle
        #     next_student_rank.rankMessage = "Set Belt from Stripe"
        #
        # # also rare, but I wanted to deal with it, there is a belt id but no stripe id
        # elif student_record.currentRankNum and not student_record.currentStripeId:
        #     requirement_record_stmt = (
        #         select(Requirements)
        #         .where(Requirements.beltId == student_record.currentRankNum)
        #         .order_by(Requirements.stripeSeqNum)
        #     )
        #     requirement_record = db_session.scalars(requirement_record_stmt).first()
        #     next_student_rank.currentRankNum = requirement_record.beltId
        #     next_student_rank.currentRankName = requirement_record.beltTitle
        #     next_student_rank.studentPromotionDate = requirement_record.promotionDate
        #     next_student_rank.rankMessage = "Set Stripe from Belt"
        #
        # # calculate based on attendance counts
        # else:
        #     attendance_counts = GetAllAttendanceCounts(student_record.badgeNumber)
        #
        #     # next_student_rank.currentRankNum = promotion_record.beltId
        #     # next_student_rank.currentRankName = promotion_record.beltTitle
        #     # next_student_rank.currentStripeId = promotion_record.stripeId
        #     # next_student_rank.currentStripeName = promotion_record.stripeTitle
        #     # next_student_rank.studentPromotionDate = promotion_record.promotionDate
        #     next_student_rank.rankMessage = "Calculated"
        #
        # # default to today, nothing else to work with
        # if not student_record.studentPromotionDate:
        #     next_student_rank.studentPromotionDate = datetime.now().strftime(constants.fmtDateTime)
        #
        # return next_student_rank

    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex




# ---------------------------------------------------------------------------------------
def GetNextFromCurrent(student_record: Students) -> StudentRankFields:
    try:
        next_student_rank = StudentRankFields.construct()
        crnt_requirement_stmt = (select(Requirements)
                                 .where(Requirements.beltId == student_record.currentRankNum)
                                 .where(Requirements.stripeId == student_record.currentStripeId)
                                 .order_by(Requirements.promotionSeqNum))
        crnt_requirement_id = db_session.scalars(crnt_requirement_stmt).first().requirementId
        next_requirement_stmt = ((select(Requirements)
                                  .where(Requirements.requirementId > crnt_requirement_id))
                                 .order_by(Requirements.promotionSeqNum))
        next_requirement_record = db_session.scalars(next_requirement_stmt).first()

        next_student_rank.currentRankNum = next_requirement_record.beltId
        next_student_rank.currentRankName = next_requirement_record.beltTitle
        next_student_rank.currentStripeId = next_requirement_record.stripeId
        next_student_rank.currentStripeName = next_requirement_record.stripeTitle
        next_student_rank.studentPromotionDate = datetime.now().strftime(constants.fmtDateTime)
        next_student_rank.rankMessage = "From current rank"
        return next_student_rank
    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

def GetNextFromLastPromotion(last_promotion_record: Promotions) -> StudentRankFields:
    try:
        next_student_rank = StudentRankFields.construct()
        crnt_requirement_stmt = (select(Requirements)
                                 .where(Requirements.beltId == last_promotion_record.beltId)
                                 .where(Requirements.stripeId == last_promotion_record.stripeId)
                                 .order_by(Requirements.promotionSeqNum))
        crnt_requirement_id = db_session.scalars(crnt_requirement_stmt).first().requirementId

        next_requirement_stmt = ((select(Requirements)
                                  .where(Requirements.requirementId > crnt_requirement_id))
                                 .order_by(Requirements.promotionSeqNum))
        next_requirement_record = db_session.scalars(next_requirement_stmt).first()

        next_student_rank.currentRankNum = next_requirement_record.beltId
        next_student_rank.currentRankName = next_requirement_record.beltTitle
        next_student_rank.currentStripeId = next_requirement_record.stripeId
        next_student_rank.currentStripeName = next_requirement_record.stripeTitle
        next_student_rank.studentPromotionDate = next_requirement_record.promotionDate
        next_student_rank.rankMessage = "From last promotion"
        return next_student_rank
    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

def GetBasedOnAttendanceTotalCount(student_record: Students) -> StudentRankFields:
    try:
        next_student_rank = StudentRankFields.construct()
        attendance_total_stmt = (select(func.count())
                                 .select_from(Attendance)
                                 .where(Attendance.badgeNumber == student_record.badgeNumber))
        attendance_count_total = db_session.scalar(attendance_total_stmt)
        requirement_record = (
            db_session.scalars(select(Requirements)
                               .where(Requirements.requiredClasses <= attendance_count_total)
                               .order_by(Requirements.beltId.desc(), Requirements.promotionSeqNum.desc()))
            .first()
        )
        next_student_rank.currentRankNum = requirement_record.beltId
        next_student_rank.currentRankName = requirement_record.beltTitle
        next_student_rank.currentStripeId = requirement_record.stripeId
        next_student_rank.currentStripeName = requirement_record.stripeTitle
        next_student_rank.rankMessage = "From total attendance"
        return next_student_rank
    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

# ---------------------------------------------------------------------------------------
def GetPromotionRecords(badge_number: int) -> list[Promotions]:
    promotion_query_stmt = (select(Promotions)
                            .where(Promotions.badgeNumber == badge_number)
                            .order_by(Promotions.promotionDate.desc())
                            )
    return db_session.scalars(promotion_query_stmt).all()

def GetLastPromotionRecord(badge_number) -> Promotions:
    promotion_record_stmt = (select(Promotions)
                             .where(Promotions.badgeNumber == badge_number)
                             .order_by(Promotions.promotionDate.desc()))
    return db_session.scalars(promotion_record_stmt).first()

