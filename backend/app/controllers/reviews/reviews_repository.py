from app.db import db
from app.models import Reviews


class ReviewsRepository:
    def __init__(self, db=db, review=Reviews):
        self.db = db
        self.review = review

    def create_review(self, data):
        return self.review(**data)

    def get_review(self, transaction_id, product_id, user_id):
        return self.review.query.filter_by(
            transaction_id=transaction_id, product_id=product_id, user_id=user_id
        ).first()
