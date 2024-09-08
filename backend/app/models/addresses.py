from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    TEXT,
    DateTime,
    ForeignKey,
    SmallInteger,
)
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
import pytz

from ..db import db


class Is_Active_Status(Enum):
    INACTIVE = 0
    ACTIVE = 1


class Addresses(db.Model):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receiver_name = Column(VARCHAR(30), nullable=False)
    phone_number = Column(VARCHAR(14), nullable=False)
    address_type = Column(VARCHAR(20), nullable=False)
    address_line = Column(TEXT, nullable=False)
    province_id = Column(SmallInteger, ForeignKey("provinces.id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    rt_rw = Column(VARCHAR(7), nullable=True)
    postal_code = Column(VARCHAR(5), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=True)
    is_active = Column(
        SmallInteger, default=Is_Active_Status.ACTIVE.value, nullable=False
    )
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.UTC))

    seller_shipment = relationship(
        "ShipmentDetails",
        foreign_keys="[ShipmentDetails.seller_address_id]",
        backref="seller_addresses",
    )
    user_shipment = relationship(
        "ShipmentDetails",
        foreign_keys="[ShipmentDetails.user_address_id]",
        backref="user_addresses",
    )

    def __init__(
        self,
        receiver_name,
        phone_number,
        address_type,
        address_line,
        province_id,
        district_id,
        postal_code,
        rt_rw,
        user_id,
        seller_id,
    ):
        self.receiver_name = receiver_name
        self.phone_number = phone_number
        self.address_type = address_type
        self.address_line = address_line
        self.province_id = province_id
        self.district_id = district_id
        self.postal_code = postal_code
        self.rt_rw = rt_rw
        self.user_id = user_id
        self.seller_id = seller_id

    def to_dict(self):
        return {
            "id": self.id,
            "receiver_name": self.receiver_name,
            "phone_number": self.phone_number,
            "address_type": self.address_type,
            "address_line": self.address_line,
            "province_id": self.province_id,
            "district_id": self.district_id,
            "province_name": self.province_addresses.province,
            "district_name": self.district_addresses.district,
            "rt_rw": self.rt_rw,
            "postal_code": self.postal_code,
            "is_active": self.is_active,
        }

    def delete_address(self):
        self.is_active = Is_Active_Status.INACTIVE.value
