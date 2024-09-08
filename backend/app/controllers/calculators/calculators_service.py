import asyncio

from ..users.users_services import UserServices

from .voucher_service import VoucherService
from .product_service import ProductService
from .shipment_service import ShipmentService
from ..shipping_options.shipping_options_service import ShippingOptionsService


class CalculatorsService:
    def __init__(
        self,
        user_service=None,
        voucher_service=None,
        product_service=None,
        shipment_service=None,
        shipping_options_service=None,
    ):
        self.user_service = user_service or UserServices()
        self.voucher_service = voucher_service or VoucherService()
        self.product_service = product_service or ProductService()
        self.shipment_service = shipment_service or ShipmentService()
        self.shipping_options_service = (
            shipping_options_service or ShippingOptionsService()
        )

    def calculate_cart(self, data, identity):
        """
        carts: [
            {
                "product_id": 1,
                "quantity": 2
                },
            {
                "product_id": 2,
                "quantity": 1
                }
                ],
        selected_user_voucher_ids: [1, 3, 5],
        user_selected_address_id: 2,
        selected_courier:
        [
            { "seller_id" : 3,
              "selected_courier": "jne",
              "selected_service": "CTCYES"},
            { "seller_id" : 4,
              "selected_courier": "jne",
              "selected_service": "CTCYES"}
        ]
        """

        try:
            carts = data.get("carts")
            user_id = identity.get("id")
            role = identity.get("role")
            user_selected_address_id = data.get("user_selected_address_id", None)
            selected_voucher = data.get("selected_user_voucher_ids", [])
            selected_courier = data.get("selected_courier", None)

            # initial verification
            self.initial_verification(role=role, carts=carts, user_id=user_id)

            # calculate product detail (total_price, volume, weight, etc)
            calculated_product_detail = self.product_service.calculate_product_detail(
                carts=carts
            )

            # check voucher and get voucher detail
            if selected_voucher and len(selected_voucher) > 0:
                voucher_list = self.voucher_service.get_sorted_vouchers(
                    selected_voucher=selected_voucher,
                    identity=identity,
                    calculated_product_detail=calculated_product_detail,
                )

                # insert discount to calculated_product_detail
                for key, value in voucher_list.items():
                    calculated_product_detail[key]["total_discount"] = value[
                        "total_discount"
                    ]
                    calculated_product_detail[key]["user_seller_voucher_id"] = value[
                        "user_seller_voucher_id"
                    ]

            # Calculated shipment fee
            if selected_courier:
                if not user_selected_address_id:
                    raise ValueError("user_selected_address_id is required")

                calculated_shipment_fee = self.calculate_shipment_fee(
                    identity=identity,
                    user_selected_address_id=user_selected_address_id,
                    selected_courier=selected_courier,
                    calculated_product_detail=calculated_product_detail,
                )

                # insert to calculated_product_detail
                for seller_id, values in calculated_shipment_fee.items():
                    for key, value in values.items():
                        calculated_product_detail[seller_id][key] = value

            # insert total with shipment fee
            final_calculation = self.calculate_final_price(
                calculated_product_detail=calculated_product_detail
            )

            return {
                "final_calculation": final_calculation.get("final_calculation"),
                "all_final_price": final_calculation.get("all_final_price", None),
            }, 200
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def calculate_final_price(self, calculated_product_detail):
        all_final_price = 0

        for key, value in calculated_product_detail.items():
            if not value.get("shipment_fee", None):
                return {"final_calculation": calculated_product_detail}

            total_price_before_shipment = int(value["total_price_before_shipment"])
            shipment_fee = int(value["shipment_fee"])
            total_discount = int(value.get("total_discount", 0))

            value["final_price"] = (
                total_price_before_shipment + shipment_fee - total_discount
            )
            all_final_price += value["final_price"]

        return {
            "final_calculation": calculated_product_detail,
            "all_final_price": all_final_price,
        }

    def initial_verification(self, role, carts, user_id):
        if role != "user":
            raise ValueError("For user only")

        if not carts:
            raise ValueError("No items in cart")

        if not self.user_service.user_info(user_id=user_id):
            raise ValueError("User not found")

    def calculate_shipment_fee(
        self,
        identity,
        user_selected_address_id,
        selected_courier,
        calculated_product_detail,
    ):
        user_district = self.shipment_service.check_selected_user_address(
            identity=identity, user_address_id=user_selected_address_id
        )["district_id"]

        all_shipment_fee = {}

        for courier in selected_courier:
            seller_ids = calculated_product_detail.keys()
            if int(courier["seller_id"]) not in seller_ids:
                raise ValueError(
                    f"selected_courier seller_id {courier['seller_id']} not in any seller_id of product in cart"
                )
            seller_id = courier["seller_id"]
            seller_address = self.shipment_service.get_seller_address(
                seller_id=seller_id
            )
            seller_address_id = seller_address["id"]
            seller_district = seller_address["district_id"]
            courier_vendor = courier["selected_courier"]

            seller_identity = {"role": "seller", "id": seller_id}
            couriers_option, status_code = (
                self.shipping_options_service.get_option_list(identity=seller_identity)
            )
            if status_code != 200:
                raise ValueError(couriers_option["error"])

            seller_courier = []
            for option in couriers_option:
                if option["is_active"] == 1:
                    seller_courier.append(option["shipment"])

            if courier_vendor not in seller_courier:
                raise ValueError(
                    f"selected_courier vendor {courier_vendor} not in any courier that provided by seller {seller_id}"
                )

            shipment_option = asyncio.run(
                self.shipment_service.get_possible_shipment_option(
                    user_district=user_district,
                    seller_district=seller_district,
                    total_weight=calculated_product_detail.get(int(seller_id)).get(
                        "total_weight_gram"
                    ),
                    courier=courier_vendor,
                )
            )

            for data in shipment_option.get(courier_vendor):
                if data["service"] == courier["selected_service"]:
                    all_shipment_fee[seller_id] = {
                        "shipment_fee": data["cost"],
                        "seller_address_id": seller_address_id,
                        "service": data["service"],
                        "etd": data["etd"],
                        "vendor_name": courier_vendor,
                    }

        return all_shipment_fee
