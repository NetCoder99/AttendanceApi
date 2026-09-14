from sqlalchemy import select

import constants
from models.data_models import Students, Requirements, Promotions
from models.input_models import NewPromotionRecord
from services.promotion_validations import ValidatePromotionParams
from services.promotions_create import InsNewPromotionRecord
from services.sqlite_alchemy import getAlchemySession

db_session = getAlchemySession()

def UpdateStudentRank(student_record: Students,  promotion_params: NewPromotionRecord):
    try:
        ValidatePromotionParams(promotion_params)
        student_record.currentRankNum = promotion_params.belt_id
        student_record.currentStripeId = promotion_params.stripe_id
        student_record.currentRankName = promotion_params.belt_name
        student_record.currentStripeName = promotion_params.stripe_name
        student_record.studentPromotionDate = promotion_params.promotion_date.strftime(constants.fmtDateTime)
        db_session.commit()
        InsNewPromotionRecord(student_record, promotion_params)
        return promotion_params
    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

def UpdateStudentRecord(student_record: Students):
    try:
        # ValidateStudentParams(promotion_params)
        pass

    except Exception as ex:
        print(f'Error: {str(ex)}')
        raise ex

