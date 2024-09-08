from app.db import db
from . import products_repository


class ProductServicesUser:
    def __init__(self, db=db, repository=None):
        self.db = db
        self.repository = repository or products_repository.ProductsRepository()

    def get_product_by_category(self, category_id, request):
        try:
            page = request.args.get("page", 1, int)
            per_page = request.args.get("per_page", 10, int)

            products = self.repository.get_product_by_category(
                category_id=category_id, page=page, per_page=per_page
            )

            if not products:
                raise ValueError("Product not found / Invalid Category ID")

            return self.response(products=products), 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def get_product_by_filter(self, req):
        rating = req.args.get("rating", None)
        price = req.args.get("price", None)
        date = req.args.get("date", None)
        category = req.args.get("category", None)
        province_id = req.args.get("province_id", None)
        district_id = req.args.get("district_id", None)
        seller_id = req.args.get("seller_id", None)

        try:
            per_page = req.args.get("per_page", 10, int)
            page = req.args.get("page", 1, int)

            products = self.repository.get_product_by_filter(
                rating=rating,
                price=price,
                date=date,
                per_page=per_page,
                page=page,
                category_id=category,
                province_id=province_id,
                district_id=district_id,
                seller_id=seller_id,
            )

            if not products:
                raise ValueError("Product not found / Invalid Filter")

            return self.response(products=products), 200

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def get_product_by_id(self, product_id):
        try:
            product = self.repository.get_product_by_id(
                role="user", product_id=product_id
            )

            if not product:
                raise ValueError("Product not found")

            return product.to_dict(), 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def response(self, products):
        return {
            "products": [product.to_dict() for product in products],
            "total_page": products.pages,
            "current_page": products.page,
            "total_items": products.total,
        }
