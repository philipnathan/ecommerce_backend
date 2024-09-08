from app.db import db
from app.models import Shipments


class ShipmentsRepository:

    def __init__(self, db=db, shipment=Shipments):
        self.db = db
        self.shipment = shipment

    def get_list_shipments(self):
        return self.shipment.query.all()

    def get_by_vendor(self, vendor_name):
        return self.shipment.query.filter_by(vendor_name=vendor_name).first()
