from .reviews_repository import ReviewsRepository
from app.db import db


class ReviewsService:
    def __init__(self, db=db, repository=None, product_repository=None):
        self.db = db
        self.repository = repository or ReviewsRepository()

    def create_review(
        self, product_id, rating, seller_id, user_id, transaction_id, review
    ):
        try:
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")

            if not seller_id or not user_id:
                raise ValueError("Seller and user id required")

            if not product_id or not transaction_id:
                raise ValueError("Product and transaction id required")

            old_review = self.repository.get_review(
                transaction_id=transaction_id, product_id=product_id, user_id=user_id
            )

            if old_review:
                raise ValueError("Product has been reviewed")

            new_review = self.repository.create_review(
                {
                    "product_id": product_id,
                    "rating": rating,
                    "seller_id": seller_id,
                    "user_id": user_id,
                    "transaction_id": transaction_id,
                    "review": review,
                }
            )

            self.db.session.add(new_review)

            return {"message": "Review created successfully"}, 201
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500
