from sqlalchemy import Column, Integer, DateTime, VARCHAR, ForeignKey, Text
from datetime import datetime
import pytz
from enum import Enum


from ..db import db


class shipment_status(Enum):
    PENDING = "pending"
    ONDELIVERY = "ondelivery"
    DELIVERED = "delivered"


class ShipmentDetails(db.Model):
    __tablename__ = "shipment_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(VARCHAR(30), ForeignKey("transactions.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    user_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    service = Column(VARCHAR(30), nullable=False)
    tracking_number = Column(VARCHAR(30), nullable=True)
    shipment_cost = Column(Integer, nullable=False)
    total_weight_gram = Column(Integer, nullable=False)
    shipment_status = Column(Text, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.UTC)
    )

    def __init__(
        self,
        transaction_id,
        seller_address_id,
        user_address_id,
        shipment_id,
        service,
        shipment_cost,
        total_weight_gram,
        user_id,
        seller_id,
        tracking_number=None,
        shipment_status=None,
    ):
        self.transaction_id = transaction_id
        self.seller_address_id = seller_address_id
        self.user_address_id = user_address_id
        self.shipment_id = shipment_id
        self.service = service
        self.tracking_number = tracking_number
        self.shipment_cost = shipment_cost
        self.total_weight_gram = total_weight_gram
        self.shipment_status = shipment_status
        self.user_id = user_id
        self.seller_id = seller_id

    def to_dict(self):
        return {
            "id": self.id,
            "tracking_number": self.tracking_number,
        }

    def shipment_to_pending(self):
        self.shipment_status = shipment_status.PENDING.value

    def shipment_to_ondelivery(self):
        self.shipment_status = shipment_status.ONDELIVERY.value

    def shipment_to_delivered(self):
        self.shipment_status = shipment_status.DELIVERED.value
