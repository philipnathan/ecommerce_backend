from datetime import datetime

from app.db import db
from .user_seller_vouchers_repository import UserSellerVouchersRepository
from ..users.users_repository import UserRepository
from ..seller_vouchers.seller_vouchers_repository import SellerVouchersRepository


class UserSellerVouchersService:
    def __init__(
        self,
        db=db,
        repository=None,
        user_repository=None,
        seller_voucher_repository=None,
    ):
        self.db = db
        self.repository = repository or UserSellerVouchersRepository()
        self.user_repository = user_repository or UserRepository()
        self.seller_voucher_repository = (
            seller_voucher_repository or SellerVouchersRepository()
        )

    def user_save_voucher(self, identity, seller_voucher_id):
        try:
            self.check_user(identity=identity)

            user_id = identity.get("id")

            if self.repository.get_voucher_by_id_and_user_id(
                user_id=user_id, seller_voucher_id=seller_voucher_id
            ):
                raise ValueError("Voucher already claimed")

            voucher = self.seller_voucher_repository.get_voucher_only_by_voucher_id(
                voucher_id=seller_voucher_id
            )

            if (
                not voucher
                or voucher.is_active == 0
                or voucher.expiry_date < datetime.now()
            ):
                raise ValueError("Voucher not found / expired / not active")

            voucher = self.repository.user_save_voucher(
                user_id=user_id, voucher_id=seller_voucher_id
            )

            self.db.session.add(voucher)
            self.db.session.commit()

            return {"message": "Voucher saved successfully"}, 201
        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            self.db.session.rollback()
            return {"error": str(e)}, 500

    def user_list_vouchers(self, identity, req):
        try:
            self.check_user(identity=identity)

            user_id = identity.get("id")
            seller_ids = req.args.getlist("sellerids", None)\
                
            if not seller_ids:
                vouchers = self.repository.get_vouchers_by_user_id(user_id=user_id)
            else:
                vouchers = self.repository.get_voucher_by_seller_ids(
                    user_id=user_id, seller_ids=seller_ids
                )

            if not vouchers:
                raise ValueError("No vouchers found")

            return [voucher.to_dict() for voucher in vouchers], 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def user_used_voucher(self, identity, user_seller_voucher_id, commit=True):
        try:
            self.check_user(identity=identity)

            user_id = identity.get("id")
            voucher = self.repository.get_voucher_by_id(
                user_seller_voucher_id=user_seller_voucher_id, user_id=user_id
            )

            if not voucher:
                raise ValueError("Voucher not found")
            if voucher.is_used == 1:
                raise ValueError("Voucher already used")

            voucher.used_voucher()

            if commit:
                self.db.session.commit()

            return {"message": "Voucher used successfully"}, 200
        except ValueError as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 500

    def user_unused_voucher(self, user_id, user_seller_voucher_id, commit=True):
        try:
            identity = {"id": user_id, "role": "user"}
            self.check_user(identity=identity)

            user_id = identity.get("id")
            voucher = self.repository.get_voucher_by_id(
                user_seller_voucher_id=user_seller_voucher_id, user_id=user_id
            )

            if not voucher:
                raise ValueError("Voucher not found")
            if voucher.is_used == 0:
                raise ValueError("Voucher already unused")

            voucher.unused_voucher()

            if commit:
                self.db.session.commit()

            return {"message": "Voucher unused successfully"}, 200
        except ValueError as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 500

    def user_voucher_details(self, identity, user_seller_voucher_id):
        try:
            self.check_user(identity=identity)

            user_id = identity.get("id")
            voucher = self.repository.get_voucher_by_id(
                user_seller_voucher_id=user_seller_voucher_id, user_id=user_id
            )

            if not voucher:
                raise ValueError("Voucher not found")

            return voucher.to_dict(), 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def check_user(self, identity):
        user_id = identity.get("id")
        role = identity.get("role")

        if role != "user":
            raise ValueError("Unauthorized")

        if self.user_repository.get_user_by_id(user_id) is None:
            raise ValueError("User not found")
