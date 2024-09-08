from app.db import db
from .payment_details_repository import PaymentDetailsRepository

import pytz
from datetime import datetime


class PaymentDetailsService:
    def __init__(self, db=db, repository=None):
        self.db = db
        self.repository = repository or PaymentDetailsRepository()

    def input_details(self, data):
        try:
            payment_transaction_id = data["transaction_id"]

            payment_details = self.repository.find_by_payment_transaction_id(
                payment_transaction_id
            )

            jakarta_tz = pytz.timezone("Asia/Jakarta")
            transaction_strp = datetime.strptime(
                data["transaction_time"], "%Y-%m-%d %H:%M:%S"
            )
            settlement_strp = (
                datetime.strptime(data["settlement_time"], "%Y-%m-%d %H:%M:%S")
                if data.get("settlement_time", None)
                else None
            )

            gross_amount = data["gross_amount"]
            payment_type = data["payment_type"]
            order_id = data["order_id"]
            transaction_status = data["transaction_status"]
            fraud_status = data["fraud_status"]
            transaction_time = jakarta_tz.localize(transaction_strp).astimezone(
                pytz.utc
            )
            settlement_time = (
                jakarta_tz.localize(settlement_strp).astimezone(pytz.utc)
                if settlement_strp
                else None
            )

            if payment_details:
                payment_details.payment_type = payment_type
                payment_details.transaction_status = transaction_status
                payment_details.fraud_status = fraud_status
                payment_details.transaction_time = transaction_time
                payment_details.settlement_time = settlement_time

                return {
                    "message": "Payment details updated successfully",
                    "details": payment_details,
                }, 200

            else:
                details = {
                    "gross_amount": gross_amount,
                    "payment_type": payment_type,
                    "order_id": order_id,
                    "payment_transaction_id": payment_transaction_id,
                    "transaction_status": transaction_status,
                    "fraud_status": fraud_status,
                    "transaction_time": transaction_time,
                    "settlement_time": settlement_time,
                }

                new_details = self.repository.input_details(details)
                self.db.session.add(new_details)

                self.db.session.commit()

                return {
                    "message": "Payment details created successfully",
                    "details": new_details,
                }, 201

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500
