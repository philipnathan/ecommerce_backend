from sqlalchemy.sql import func

from app.db import db
from app.models import Products, Reviews, Addresses


class ProductsRepository:
    def __init__(self, db=db, product=Products, address=Addresses):
        self.db = db
        self.product = product
        self.address = address

    def create_product(self, seller_id, **data):
        return self.product(seller_id=seller_id, **data)

    def get_list_products(self, role, page, per_page, role_id=None):
        if role == "seller":
            return self.product.query.filter_by(seller_id=role_id).paginate(
                page=page, per_page=per_page
            )

        if role == "user":
            return self.product.query.filter_by(is_active=1).paginate(
                page=page, per_page=per_page
            )

    def get_product_by_id(self, role, product_id, role_id=None):
        if role == "seller":
            return self.product.query.filter_by(
                seller_id=role_id, id=product_id
            ).first()

        if role == "user":
            return self.product.query.filter_by(is_active=1, id=product_id).first()

    def get_product_by_category(self, category_id, page, per_page):
        return self.product.query.filter_by(
            category_id=category_id, is_active=1
        ).paginate(page=page, per_page=per_page)

    def get_product_by_filter(
        self,
        page,
        per_page,
        rating=None,
        price=None,
        date=None,
        category_id=None,
        province_id=None,
        district_id=None,
        seller_id=None,
    ):
        query = self.product.query

        if rating:
            query = (
                query.outerjoin(Reviews, self.product.id == Reviews.product_id)
                .group_by(self.product.id)
                .filter(self.product.is_active == 1)
            )

            if rating == "asc":
                query = query.order_by(func.coalesce(func.avg(Reviews.rating), 0).asc())
            if rating == "desc":
                query = query.order_by(
                    func.coalesce(func.avg(Reviews.rating), 0).desc()
                )

        if category_id:
            query = query.filter(self.product.category_id == category_id)
        if price == "asc":
            query = query.order_by(self.product.price.asc())
        if price == "desc":
            query = query.order_by(self.product.price.desc())
        if date == "newest":
            query = query.order_by(self.product.created_at.desc())
        if date == "oldest":
            query = query.order_by(self.product.created_at.asc())
        if province_id:
            query = (
                query.join(Addresses, self.product.seller_id == Addresses.seller_id)
                .group_by(self.product.id)
                .filter(Addresses.province_id == province_id)
            )
        if district_id:
            query = (
                query.join(Addresses, self.product.seller_id == Addresses.seller_id)
                .group_by(self.product.id)
                .filter(Addresses.district_id == district_id)
            )
        if seller_id:
            query = query.filter(self.product.seller_id == seller_id)

        return query.paginate(page=page, per_page=per_page)
