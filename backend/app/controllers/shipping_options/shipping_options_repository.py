from app.db import db
from app.models import ShippingOptions


class ShippingOptionsRepository:

    def __init__(self, db=db, shipping_option=ShippingOptions):
        self.db = db
        self.option = shipping_option

    def get_options_by_shipment_id(self, seller_id, shipment_id):
        return self.option.query.filter_by(
            seller_id=seller_id, shipment_id=shipment_id
        ).first()

    def create_shipping_option(self, shipment_id, seller_id, is_active):
        return self.option(
            shipment_id=shipment_id, seller_id=seller_id, is_active=is_active
        )

    def get_list_options(self, seller_id):
        return self.option.query.filter_by(seller_id=seller_id).all()
