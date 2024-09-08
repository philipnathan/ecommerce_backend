from app.db import db
from app.models import ProductOrders


class ProductOrdersRepository:

    def __init__(self, db=db, product_order=ProductOrders):
        self.db = db
        self.product_order = product_order

    def create_product_order(self, data):
        return self.product_order(**data)

    def get_product_orders_by_transaction_id(self, transaction_id):
        return self.product_order.query.filter_by(transaction_id=transaction_id).all()
