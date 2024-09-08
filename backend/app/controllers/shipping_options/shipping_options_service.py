from app.db import db
from .shipping_options_repository import ShippingOptionsRepository

from ..shipments.shipments_repository import ShipmentsRepository


class ShippingOptionsService:

    def __init__(self, db=db, repository=None, shipment_repository=None):
        self.db = db
        self.repository = repository or ShippingOptionsRepository()
        self.shipment_repository = shipment_repository or ShipmentsRepository()

    def update_option(self, data, identity):
        try:
            role = identity.get("role")
            role_id = identity.get("id")

            shipment_status = data.get("shipment_status")

            if role != "seller":
                return {"error": "Unauthorized"}, 401

            for key, value in shipment_status.items():
                shipment = self.shipment_repository.get_by_vendor(vendor_name=key)

                if not shipment:
                    raise ValueError(f"Vendor {key} not found")

                option = self.repository.get_options_by_shipment_id(
                    seller_id=role_id, shipment_id=shipment.id
                )

                if option:
                    setattr(option, "is_active", value)
                else:
                    new_option = self.repository.create_shipping_option(
                        shipment_id=shipment.id, seller_id=role_id, is_active=value
                    )

                    self.db.session.add(new_option)

            self.db.session.commit()

            return {"message": "Options created/updated successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def get_option_list(self, identity):
        try:
            role = identity.get("role")
            role_id = identity.get("id")

            if role != "seller":
                return {"error": "Unauthorized"}, 401

            options = self.repository.get_list_options(seller_id=role_id)

            return [option.to_dict() for option in options], 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500
