from app.db import db
from app.models import PaymentDetails


class PaymentDetailsRepository:
    def __init__(self, db=db, payment_details=PaymentDetails):
        self.db = db
        self.payment_details = payment_details

    def input_details(self, details):
        new_details = self.payment_details(**details)

        return new_details

    def find_by_payment_transaction_id(self, payment_transaction_id):
        return self.payment_details.query.filter_by(
            payment_transaction_id=payment_transaction_id
        ).first()
