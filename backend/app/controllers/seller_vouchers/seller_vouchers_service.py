from datetime import datetime, timezone

from .seller_vouchers_repository import SellerVouchersRepository
from app.db import db
from ..common import is_filled, get_data_and_validate, change_date


class SellerVouchersService:
    def __init__(self, db=db, repository=None):
        self.repository = repository or SellerVouchersRepository()
        self.db = db

    def create_voucher(self, data, identity):
        try:
            keys = [
                "title",
                "discount_type",
                "min_purchase_amount",
                "max_discount_amount",
                "usage_limit",
                "start_date",
                "expiry_date",
            ]
            start_date = data.get("start_date")
            expiry_date = data.get("expiry_date")
            tz = data.get("timezone", None)

            data = self.get_all_data(data)

            if not is_filled(**data):
                raise ValueError("Please fill all required fields")

            for key in keys:
                if key not in data:
                    raise ValueError(f"{key} is required")

            if data["discount_type"] == 1 and "percentage" not in data:
                raise ValueError("Please fill percentage")
            if data["discount_type"] == 2:
                data["percentage"] = None

            if not tz:
                raise ValueError("Please provide timezone")

            if identity.get("role") != "seller":
                raise ValueError("Unauthorized")

            data["seller_id"] = identity.get("id")

            data["start_date"] = change_date(start_date, tz)
            data["expiry_date"] = change_date(expiry_date, tz)

            if data["start_date"] > data["expiry_date"]:
                raise ValueError("Start date must be less than expiry date")
            if data["start_date"] < datetime.now(timezone.utc):
                raise ValueError(
                    "Start date must be greater than or equal to current date and time"
                )

            voucher = self.repository.create_voucher(data)

            self.db.session.add(voucher)
            self.db.session.commit()

            return {"message": "Voucher created successfully"}, 201
        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def list_vouchers(self, identity, req):
        try:
            if identity.get("role") != "seller":
                raise ValueError("Unauthorized")

            date = req.args.get("date", "latest")
            per_page = req.args.get("per_page", 10, int)
            page = req.args.get("page", 1, int)

            seller_id = identity.get("id")
            vouchers = self.repository.list_vouchers(
                seller_id=seller_id, date=date, page=page, per_page=per_page
            )

            return [voucher.to_dict() for voucher in vouchers], 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def voucher_detail(self, voucher_id, identity):
        try:
            if identity.get("role") != "seller":
                raise ValueError("Unauthorized")

            seller_id = identity.get("id")
            voucher = self.repository.get_voucher_by_id(
                voucher_id=voucher_id, seller_id=seller_id
            )

            if not voucher:
                raise ValueError("Voucher not found")

            return voucher.to_dict(), 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def update_voucher(self, data, identity, voucher_id):
        try:
            if identity.get("role") != "seller":
                raise ValueError("Unauthorized")

            key_updated = []
            count_updated_key = 0
            data = self.get_all_data(data)
            seller_id = identity.get("id")
            voucher = self.repository.get_voucher_by_id(
                voucher_id=voucher_id, seller_id=seller_id
            )

            if not voucher:
                raise ValueError("Voucher not found")

            if voucher.is_active == 0:
                raise ValueError("Voucher already deleted. Please create a new one")

            for key, value in data.items():
                if value is not None:
                    setattr(voucher, key, value)
                    key_updated.append(key)
                    count_updated_key += 1

            if count_updated_key == 0:
                raise ValueError("No data to update")

            self.db.session.commit()

            return {
                "message": "Voucher updated successfully",
                "key_updated": key_updated,
            }, 200

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def delete_voucher(self, voucher_id, identity):
        try:
            seller_id = identity.get("id")

            if identity.get("role") != "seller":
                raise ValueError("Unauthorized")

            voucher = self.repository.get_voucher_by_id(
                voucher_id=voucher_id, seller_id=seller_id
            )

            if not voucher:
                raise ValueError("Voucher not found")

            voucher.delete_voucher()
            self.db.session.commit()

            return {"message": "Voucher deleted successfully"}, 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def get_all_data(self, data):
        return get_data_and_validate(
            data,
            title=str,
            discount_type=int,
            percentage=int,
            min_purchase_amount=int,
            max_discount_amount=int,
            usage_limit=int,
            start_date=datetime,
            expiry_date=datetime,
        )

    def get_list_voucher(self, seller_id, req):
        try:
            page = req.args.get("page", 1, int)
            per_page = req.args.get("per_page", 10, int)
            date = req.args.get("date", "latest")

            list_vouchers = self.repository.list_vouchers(
                seller_id=seller_id, page=page, per_page=per_page, date=date
            )

            if not list_vouchers:
                return [], 200

            return [voucher.to_dict() for voucher in list_vouchers], 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500
