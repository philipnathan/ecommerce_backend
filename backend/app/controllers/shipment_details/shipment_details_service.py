from app.db import db
from .shipment_details_repository import ShipmentDetailsRepository
from ..shipments.shipments_service import ShipmentsService
from ..sellers.sellers_service import SellersServices


class ShipmentDetailsService:

    def __init__(
        self,
        db=db,
        seller_service=None,
        shipment_service=None,
        repository=None,
        transaction_service_update=None,
    ):
        self.db = db
        self.repository = repository or ShipmentDetailsRepository()
        self.shipment_service = shipment_service or ShipmentsService()
        self.seller_service = seller_service or SellersServices()

    def create_detail(self, data, user_address_id, transaction_id, user_id, seller_id):
        try:
            shipments = self.shipment_service.list_shipments()
            shipments = {
                shipment["vendor_name"]: shipment["id"] for shipment in shipments
            }

            shipment_id = shipments.get(data.get("vendor_name"))
            seller_address_id = data.get("seller_address_id")
            service = data.get("service")
            shipment_cost = data.get("shipment_fee")
            total_weight_gram = data.get("total_weight_gram")
            user_address_id = user_address_id

            new_shipment_detail = self.repository.create_shipment_detail(
                {
                    "transaction_id": transaction_id,
                    "seller_address_id": seller_address_id,
                    "service": service,
                    "shipment_cost": shipment_cost,
                    "total_weight_gram": total_weight_gram,
                    "user_address_id": user_address_id,
                    "shipment_id": shipment_id,
                    "user_id": user_id,
                    "seller_id": seller_id,
                },
            )

            self.db.session.add(new_shipment_detail)
            self.db.session.commit()

            return {"message": "Shipment detail created successfully"}, 201

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def delete_detail(self, transaction_id):
        try:
            self.repository.delete_shipment_detail(transaction_id=transaction_id)

            self.db.session.commit()
            return {"message": "Shipment detail deleted successfully"}, 200
        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def update_tracking_number(self, seller_id, transaction_id, tracking_number):
        try:
            shipment_detail = self.repository.get_by_seller_and_transaction(
                seller_id=seller_id, transaction_id=transaction_id
            )

            if not shipment_detail:
                raise ValueError("Shipment detail not found")
            if shipment_detail.tracking_number:
                raise ValueError("Shipment detail already has a tracking number")

            shipment_detail.tracking_number = tracking_number
            shipment_detail.shipment_to_ondelivery()
            self.db.session.commit()

            return {"message": "Shipment detail updated successfully"}, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def update_to_delivered(self, user_id, transaction_id):
        try:
            shipment_detail = self.repository.get_by_user_and_transaction(
                user_id=user_id, transaction_id=transaction_id
            )

            if not shipment_detail:
                raise ValueError("Shipment detail not found")
            if not shipment_detail.shipment_status:
                raise ValueError("Package is not on delivery yet")
            if shipment_detail.shipment_status == "delivered":
                raise ValueError("Package is already delivered")

            shipment_detail.shipment_to_delivered()

            return {"message": "Shipment detail updated successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500
