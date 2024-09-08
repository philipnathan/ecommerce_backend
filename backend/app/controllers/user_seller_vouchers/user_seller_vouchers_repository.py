from datetime import datetime, timezone

from app.db import db
from app.models import UserSellerVouchers
from app.models import SellerVouchers


class UserSellerVouchersRepository:
    def __init__(self, db=db, voucher=UserSellerVouchers):
        self.db = db
        self.voucher = voucher

    def user_save_voucher(self, user_id, voucher_id):
        return self.voucher(user_id=user_id, seller_voucher_id=voucher_id)

    def get_vouchers_by_user_id(self, user_id):
        return self.join_query().filter(self.voucher.user_id == user_id).all()

    def get_voucher_by_id_and_user_id(self, user_id, seller_voucher_id):
        return (
            self.join_query()
            .filter(
                self.voucher.user_id == user_id,
                self.voucher.seller_voucher_id == seller_voucher_id,
            )
            .first()
        )

    def get_voucher_by_seller_ids(self, user_id, seller_ids):
        return (
            self.join_query()
            .filter(
                self.voucher.user_id == user_id,
                SellerVouchers.seller_id.in_(seller_ids),
                SellerVouchers.expiry_date >= datetime.now(timezone.utc),
            )
            .all()
        )

    def get_voucher_by_id(self, user_seller_voucher_id, user_id):
        return (
            self.join_query()
            .filter(
                self.voucher.id == user_seller_voucher_id,
                self.voucher.user_id == user_id,
            )
            .first()
        )

    def join_query(self):
        today = datetime.now(timezone.utc)

        return self.voucher.query.join(
            SellerVouchers, self.voucher.seller_voucher_id == SellerVouchers.id
        ).filter(SellerVouchers.expiry_date >= today)
