from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    SmallInteger,
    DateTime,
    VARCHAR,
)
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
import pytz

from ..db import db


class Discount_Type(Enum):
    PERCENTAGE = 1
    FIXED_DISCOUNT = 2


class Is_Active_Status(Enum):
    INACTIVE = 0
    ACTIVE = 1


class SellerVouchers(db.Model):
    __tablename__ = "seller_vouchers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    title = Column(VARCHAR(50), nullable=False)
    discount_type = Column(Integer, nullable=False)
    percentage = Column(SmallInteger, default=0, nullable=False)
    min_purchase_amount = Column(Integer, nullable=False)
    max_discount_amount = Column(Integer, nullable=False)
    usage_limit = Column(SmallInteger, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Integer, default=Is_Active_Status.ACTIVE.value, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.UTC)
    )

    seller_voucher_id = relationship("UserSellerVouchers", backref="seller_voucher")

    def to_dict(self):
        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "title": self.title,
            "discount_type": self.discount_type,
            "discount_type_name": Discount_Type(self.discount_type).name,
            "percentage": self.percentage,
            "min_purchase_amount": self.min_purchase_amount,
            "max_discount_amount": self.max_discount_amount,
            "usage_limit": self.usage_limit,
            "start_date": self.start_date,
            "expiry_date": self.expiry_date,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    def delete_voucher(self):
        self.is_active = Is_Active_Status.INACTIVE.value
