from app.db import db
from .product_orders_repository import ProductOrdersRepository


class ProductOrdersService:
    def __init__(self, db=db, repository=None):
        self.db = db
        self.repository = repository or ProductOrdersRepository()

    def get_product_orders_by_transaction_id(self, transaction_id):
        try:
            product_orders = self.repository.get_product_orders_by_transaction_id(
                transaction_id
            )

            if not product_orders:
                raise ValueError("Product order not found")

            return [product_order.to_dict() for product_order in product_orders], 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def create_product_order(self, data, transaction_id, commit=True):
        # data details dari 1 seller id
        try:
            all_data = []
            for item in data["items"]:
                specific_data = self.get_specific_data(item)
                specific_data["transaction_id"] = transaction_id

                new_data = self.repository.create_product_order(specific_data)
                all_data.append(new_data)

            self.db.session.add_all(all_data)

            if commit:
                self.db.session.commit()

            return {"message": "Product order created successfully"}, 201

        except ValueError as e:
            self.db.session.rollback()
            return {"error": str(e)}, 400
        except Exception as e:
            if commit:
                self.db.session.rollback()
            return {"error": str(e)}, 500

    def get_specific_data(self, item):
        product_id = item["detail_product"]["id"]
        quantity = item["quantity"]

        return {"product_id": product_id, "quantity": quantity}
