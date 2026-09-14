# ---------------------------------------------------------------------------------------
import constants
from models.data_models import Students, Promotions
from models.input_models import NewPromotionRecord
from services.promotion_validations import ValidatePromotionParams
from services.sqlite_alchemy import getAlchemySession
from datetime import datetime

db_session = getAlchemySession()

def InsNewPromotionRecord(student_record: Students,  promotion_params: NewPromotionRecord) -> Promotions:
    try:
        ValidatePromotionParams(promotion_params)
        new_promotion_record = Promotions()
        new_promotion_record.studentName      = f'{student_record.firstName} {student_record.lastName}'
        new_promotion_record.studentFirstName = student_record.firstName
        new_promotion_record.studentLastName  = student_record.lastName
        new_promotion_record.badgeNumber      = student_record.badgeNumber
        new_promotion_record.beltId      = promotion_params.belt_id
        new_promotion_record.beltTitle   = promotion_params.belt_name
        new_promotion_record.stripeId    = promotion_params.stripe_id
        new_promotion_record.stripeTitle = promotion_params.stripe_name
        if promotion_params.belt_id != student_record.currentRankNum:
            new_promotion_record.promotionType = 'Belt'
        else:
            new_promotion_record.promotionType = 'Stripe'
        if promotion_params.comments == '':
            new_promotion_record.comments = "Promotion from api"
        else:
            new_promotion_record.comments = promotion_params.comments
        new_promotion_record.promotionDate  = promotion_params.promotion_date.strftime(constants.fmtDateTime)
        new_promotion_record.createDateTime = datetime.now().strftime(constants.fmtDateTime)
        new_promotion_record.createDateTime = datetime.now().strftime(constants.fmtDateTime)
        db_session.add(new_promotion_record)
        db_session.commit()
        return new_promotion_record
    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

