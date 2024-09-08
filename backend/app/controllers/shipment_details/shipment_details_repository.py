from app.db import db
from app.models import ShipmentDetails


class ShipmentDetailsRepository:

    def __init__(self, db=db, shipment_details=ShipmentDetails):
        self.db = db
        self.shipment_details = shipment_details

    def create_shipment_detail(self, data):
        return self.shipment_details(**data)

    def delete_shipment_detail(self, transaction_id):
        self.shipment_details.query.filter_by(transaction_id=transaction_id).delete()

    def get_by_seller_and_transaction(self, seller_id, transaction_id):
        return self.shipment_details.query.filter_by(
            seller_id=seller_id, transaction_id=transaction_id
        ).first()

    def get_by_user_and_transaction(self, user_id, transaction_id):
        return self.shipment_details.query.filter_by(
            user_id=user_id, transaction_id=transaction_id
        ).first()
