from datetime import datetime
import pytz
from sqlalchemy.orm import relationship

from ..db import db


class PaymentDetails(db.Model):
    __tablename__ = "payment_details"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gross_amount = db.Column(db.Integer, nullable=False)
    payment_type = db.Column(db.String(30), nullable=False)
    order_id = db.Column(db.String(30), nullable=False)
    payment_transaction_id = db.Column(db.String(50), nullable=False)
    transaction_status = db.Column(db.String(30), nullable=False)
    fraud_status = db.Column(db.String(30), nullable=False)
    transaction_time = db.Column(db.DateTime, nullable=False)
    settlement_time = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC)
    )
    updated_at = db.Column(
        db.DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.UTC)
    )

    transactions = relationship("Transactions", backref="payment_details_transactions")

    def __init__(
        self,
        gross_amount,
        payment_type,
        order_id,
        payment_transaction_id,
        transaction_status,
        fraud_status,
        transaction_time,
        settlement_time=None,
    ):
        self.gross_amount = gross_amount
        self.payment_type = payment_type
        self.order_id = order_id
        self.payment_transaction_id = payment_transaction_id
        self.transaction_status = transaction_status
        self.fraud_status = fraud_status
        self.transaction_time = transaction_time
        self.settlement_time = settlement_time

    def to_dict(self):
        return {
            "id": self.id,
            "gross_amount": self.gross_amount,
            "payment_type": self.payment_type,
            "order_id": self.order_id,
            "transaction_time": self.transaction_time,
            "settlement_time": self.settlement_time,
        }
