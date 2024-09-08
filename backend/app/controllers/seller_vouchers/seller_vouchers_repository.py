from app.db import db
from app.models import SellerVouchers


class SellerVouchersRepository:
    def __init__(self, db=db, voucher=SellerVouchers):
        self.db = db
        self.voucher = voucher

    def create_voucher(self, data):
        return self.voucher(**data)

    def list_vouchers(self, seller_id, page, per_page, date):
        query = self.voucher.query.filter_by(seller_id=seller_id)

        if date == "latest":
            query = query.order_by(self.voucher.created_at.desc())
        if date == "oldest":
            query = query.order_by(self.voucher.created_at.asc())

        return query.paginate(page=page, per_page=per_page)

    def get_voucher_by_id(self, voucher_id, seller_id):
        return self.voucher.query.filter_by(id=voucher_id, seller_id=seller_id).first()

    def get_voucher_only_by_voucher_id(self, voucher_id):
        return self.voucher.query.filter_by(id=voucher_id).first()
