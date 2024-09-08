from app.db import db

from ..user_seller_vouchers.user_seller_vouchers_service import (
    UserSellerVouchersService,
)


class TransactionsVoucherService:

    def __init__(self, db=db, user_seller_vouchers_service=None):
        self.db = db
        self.user_seller_vouchers_service = (
            user_seller_vouchers_service or UserSellerVouchersService()
        )

    def used_user_seller_voucher(self, identity, data):
        try:
            user_voucher_ids = data.get("selected_user_voucher_ids")

            for user_voucher_id in user_voucher_ids:
                self.user_seller_vouchers_service.user_used_voucher(
                    identity=identity,
                    user_seller_voucher_id=user_voucher_id,
                    commit=False,
                )
        except Exception as e:
            return {"error": str(e)}, 500

    def unused_user_seller_voucher(self, user_id, user_seller_voucher_id):
        try:
            unused, status_code = self.user_seller_vouchers_service.user_unused_voucher(
                user_id=user_id,
                user_seller_voucher_id=user_seller_voucher_id,
                commit=False,
            )

            if status_code != 200:
                raise ValueError(unused["error"])

            return {"success": True}, 200

        except Exception as e:
            return {"error": str(e)}, 500
