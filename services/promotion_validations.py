from sqlalchemy import select

from models.data_models import Requirements, Promotions
from models.input_models import NewPromotionRecord
from services.sqlite_alchemy import getAlchemySession

db_session = getAlchemySession()

def ValidatePromotionParams(promotion_params: NewPromotionRecord):
    belt_record = db_session.scalars(
        select(Requirements).where(Requirements.beltId == promotion_params.belt_id)
    ).first()
    if not belt_record:
        raise Exception(f"Belt Id was not found: {promotion_params.belt_id}.")
    promotion_params.belt_name = belt_record.beltTitle

    stripe_record = db_session.scalars(
        select(Requirements).where(Requirements.stripeId == promotion_params.stripe_id)
    ).first()
    if not stripe_record:
        raise Exception(f"Stripe Id was not found: {promotion_params.stripe_id}.")
    promotion_params.stripe_name = stripe_record.stripeTitle

    requirement_record = db_session.scalars(
        select(Requirements)
        .where(Requirements.beltId == promotion_params.belt_id)
        .where(Requirements.stripeId == promotion_params.stripe_id)
    ).all()
    if not requirement_record:
        raise Exception(f"Stripe Id was not valid for that belt id: {promotion_params.belt_id}:{promotion_params.stripe_id}.")

    duplicate_record = db_session.scalars(
        select(Promotions)
        .where(Promotions.badgeNumber == promotion_params.badge_number)
        .where(Promotions.beltId      == promotion_params.belt_id)
        .where(Promotions.stripeId    == promotion_params.stripe_id)
    ).first()
    if duplicate_record:
        raise Exception(f"Duplicated promotion record not inserted: {duplicate_record.promotionId} .")

    return True