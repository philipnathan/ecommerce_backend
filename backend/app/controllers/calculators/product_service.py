from ..products.product_services_user import ProductServicesUser
from ..products.products_repository import ProductsRepository


class ProductService:
    def __init__(self, product_service_user=None, product_repository=None):
        self.product_repository = product_repository or ProductsRepository()
        self.product_service_user = product_service_user or ProductServicesUser()

    def calculate_product_detail(self, carts):
        return_value = {}
        sub_total_weight = 0
        sub_total_volume_to_weight = 0
        sorted_cart = self.split_to_each_seller(carts=carts)

        for seller_id, products in sorted_cart.items():
            return_value[seller_id] = {
                "items": [],
                "total_price_before_shipment": 0,
            }

            for product in products:

                product_detail, status_code = (
                    self.product_service_user.get_product_by_id(
                        product_id=product["id"]
                    )
                )

                if status_code != 200:
                    raise ValueError(f"Product with id: {product['id']} not found")

                if product_detail["stock"] < product["quantity"]:
                    raise ValueError(
                        f"Insufficient quantity for product with id: {product['id']}"
                    )

                sub_total = product_detail["price"] * product["quantity"]
                sub_weight = product_detail["weight_kg"] * product["quantity"]
                sub_volume = product_detail["volume_m3"] * product["quantity"]
                sub_volume_to_weight = (product_detail["volume_m3"] * 1_000_000) / 5000

                return_value[seller_id]["items"].append(
                    {
                        "detail_product": self.sorted_detail_product(product_detail),
                        "quantity": product["quantity"],
                        "sub_total": sub_total,
                        "sub_weight": sub_weight,
                        "sub_volume": sub_volume,
                        "sub_volume_to_weight": sub_volume_to_weight,
                    }
                )

                sub_total_weight += sub_weight
                sub_total_volume_to_weight += sub_volume_to_weight

                return_value[seller_id]["total_price_before_shipment"] += sub_total

            if sub_total_weight > sub_total_volume_to_weight:
                return_value[seller_id]["total_weight_gram"] = sub_total_weight * 1000
            else:
                return_value[seller_id]["total_weight_gram"] = (
                    sub_total_volume_to_weight * 1000
                )

        return return_value

    def sorted_detail_product(self, detail_product):
        sorted_detail_product = {}
        keys = [
            "category_id",
            "id",
            "image_url",
            "is_active",
            "name",
            "price",
            "product_type",
            "weight_kg",
            "volume_m3",
            "seller_info",
            "seller_id",
        ]

        for key in keys:
            sorted_detail_product[key] = detail_product[key]

        return sorted_detail_product

    def split_to_each_seller(self, carts):
        sorted_carts = {}

        for item in carts:
            product = self.product_service_user.get_product_by_id(
                product_id=item["product_id"]
            )

            if not product:
                raise ValueError(f"Product with id: {item['product_id']} not found")

            product = product[0]

            seller_id = product["seller_id"]
            product["quantity"] = item["quantity"]

            if seller_id not in sorted_carts:
                sorted_carts[seller_id] = []

            sorted_carts[seller_id].append(product)

        return sorted_carts
