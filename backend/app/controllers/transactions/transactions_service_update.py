from app.db import db
from ..sellers.sellers_service import SellersServices
from .transactions_repository import TransactionsRepository
from ..shipment_details.shipment_details_service import ShipmentDetailsService
from ..users.users_services import UserServices
from ..reviews.reviews_service import ReviewsService


class TransactionServiceUpdate:
    def __init__(
        self,
        db=db,
        repository=None,
        seller_service=None,
        shipment_details_service=None,
        user_service=None,
        review_service=None,
    ):
        self.db = db
        self.repository = repository or TransactionsRepository()
        self.seller_service = seller_service or SellersServices()
        self.shipment_details_service = (
            shipment_details_service or ShipmentDetailsService()
        )
        self.user_service = user_service or UserServices()
        self.review_service = review_service or ReviewsService()

    def change_to_prepared(self, identity, transaction_id):
        try:
            self.check_role(identity=identity)

            transaction = self.repository.get_transaction_by_id(
                transaction_id=transaction_id, role="seller", role_id=identity.get("id")
            )

            if not transaction:
                raise ValueError("Transaction not found")

            transaction.change_to_prepared()
            self.db.session.commit()

            return {"message": "Transaction changed to prepared successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def update_tracking_number(self, transaction_id, identity, data):
        try:
            self.check_role(identity=identity)

            messsage, status_code = (
                self.shipment_details_service.update_tracking_number(
                    seller_id=identity.get("id"),
                    transaction_id=transaction_id,
                    tracking_number=data.get("tracking_number"),
                )
            )

            if status_code != 200:
                raise ValueError(messsage["error"])

            transaction = self.repository.get_transaction_by_id(
                transaction_id=transaction_id, role="seller", role_id=identity.get("id")
            )

            transaction.change_to_on_delivery()
            self.db.session.commit()

            return {
                "message": "Tracking number and transaction status updated successfully"
            }, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def update_to_delivered(self, identity, transaction_id):
        try:
            self.check_user(identity=identity)
            role_id = identity.get("id")

            message, status_code = self.shipment_details_service.update_to_delivered(
                user_id=role_id, transaction_id=transaction_id
            )

            if status_code != 200:
                raise ValueError(message["error"])

            transaction = self.repository.get_transaction_by_id(
                transaction_id=transaction_id, role="user", role_id=role_id
            )

            self.seller_service.add_balanced_transaction_delivered(
                seller_id=transaction.seller_id, amount=transaction.gross_amount
            )

            transaction.change_to_delivered()
            self.db.session.commit()

            return {"message": "Transaction changed to delivered successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def create_review(self, data, transaction_id, identity):
        try:
            """
            "reviews": [
                {
                    "product_id": 1,
                    "review": "Nice product",
                    "rating": 5
                },
                {
                    "product_id": 2,
                    "review": "Bad product",
                    "rating": 1
                }
            ]
            """
            self.check_user(identity)
            role_id = identity.get("id")
            role = identity.get("role")
            reviews = data.get("reviews")

            if not reviews or len(reviews) == 0:
                raise ValueError("Please provide at least one review")

            transactions = self.repository.get_transaction_by_user_id(
                role=role, role_id=role_id, tx=transaction_id
            )

            if not transactions.items:
                raise ValueError("Transaction not found")

            transaction = [transaction.to_dict() for transaction in transactions]
            transaction = transaction[0]

            if transaction["transaction_status"] != 5:
                raise ValueError("Transaction is not delivered yet")

            product_orders = transaction["product_orders"]
            product_id = [product_id["product_id"] for product_id in product_orders]
            seller_id = transaction["seller_id"]

            for review in reviews:
                if int(review["product_id"]) not in product_id:
                    raise ValueError("Product not found in user's transaction")
                if not review["rating"]:
                    raise ValueError("Rating cannot be lower than 1 or empty")
                if int(review["rating"]) <= 0 or int(review["rating"]) > 5:
                    raise ValueError("Rating must be between 1 and 5")

                new_review, status_code = self.review_service.create_review(
                    product_id=review["product_id"],
                    review=review.get("review", None),
                    rating=review["rating"],
                    seller_id=seller_id,
                    user_id=role_id,
                    transaction_id=transaction_id,
                )

                if status_code != 201:
                    raise ValueError(new_review["error"])

            self.db.session.commit()
            return {"message": "Review created successfully"}, 201

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def check_role(self, identity):
        role = identity.get("role")
        role_id = identity.get("id")

        if role != "seller":
            raise ValueError("Unauthorized")

        seller, status_code = self.seller_service.seller_info(seller_id=role_id)

        if status_code != 200:
            raise ValueError(seller["error"])

    def check_user(self, identity):
        role = identity.get("role")
        role_id = identity.get("id")

        if role != "user":
            raise ValueError("Unauthorized")

        user, status_code = self.user_service.user_info(user_id=role_id)

        if status_code != 200:
            raise ValueError(user["error"])
