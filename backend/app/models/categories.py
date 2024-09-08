from sqlalchemy import Column, VARCHAR, SmallInteger, DateTime
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
import pytz

from ..db import db


class Is_Active_Status(Enum):
    INACTIVE = 0
    ACTIVE = 1


class Categories(db.Model):
    __tablename__ = "categories"

    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    category_name = Column(VARCHAR(30), unique=True, nullable=False)
    is_active = Column(
        SmallInteger, default=Is_Active_Status.ACTIVE.value, nullable=False
    )
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(pytz.UTC)
    )

    products = relationship("Products", backref="category_products")

    def __init__(self, category_name):
        self.category_name = category_name

    def to_dict(self):
        return {"id": self.id, "category_name": self.category_name}

    def delete_category(self):
        self.is_active = Is_Active_Status.INACTIVE.value
