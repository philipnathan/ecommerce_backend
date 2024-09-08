from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    VARCHAR,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

from ..db import db


class Shipments(db.Model):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_name = Column(VARCHAR(30), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.UTC)
    )

    shipping_options = relationship("ShippingOptions", backref="shipment_options")
    shipment_details = relationship("ShipmentDetails", backref="shipment_details")

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_name": self.vendor_name,
        }
