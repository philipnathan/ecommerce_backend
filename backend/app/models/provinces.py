from sqlalchemy import Column, SmallInteger, VARCHAR, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

from ..db import db


class Provinces(db.Model):
    __tablename__ = "provinces"

    id = Column(SmallInteger, primary_key=True, autoincrement=False)
    province = Column(VARCHAR(100), unique=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(pytz.UTC), nullable=False
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.UTC)
    )

    district = relationship("Districts", backref="province_districts")
    addresses = relationship("Addresses", backref="province_addresses")

    def provinces_to_dict(self):
        return {"province": self.province}

    def to_dict(self):
        return {
            "id": self.id,
            "province": self.province,
        }
