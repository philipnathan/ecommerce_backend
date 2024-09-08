from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    Text,
    DateTime,
    ForeignKey,
    VARCHAR,
)
from datetime import datetime
import pytz

from app.db import db


class Reviews(db.Model):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    review = Column(Text, nullable=True)
    transaction_id = Column(VARCHAR(30), ForeignKey("transactions.id"), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC)
    )

    def __init__(self, product_id, seller_id, user_id, rating, review, transaction_id):
        self.product_id = product_id
        self.seller_id = seller_id
        self.user_id = user_id
        self.rating = rating
        self.review = review
        self.transaction_id = transaction_id

    def to_dict(self):
        user_username = self.user_reviews.to_dict()["username"]

        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_username": user_username,
            "rating": round(self.rating, 0),
            "review": self.review,
        }
