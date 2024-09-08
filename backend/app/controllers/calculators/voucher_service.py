from datetime import datetime

from ..user_seller_vouchers.user_seller_vouchers_service import (
    UserSellerVouchersService,
)


class VoucherService:
    def __init__(self, user_voucher_service=None):
        self.user_voucher_service = user_voucher_service or UserSellerVouchersService()

    def get_sorted_vouchers(
        self, selected_voucher, identity, calculated_product_detail
    ):
        voucher_list = {}
        list_seller_id = list(calculated_product_detail.keys())

        for voucher_id in selected_voucher:
            voucher, status_code = self.user_voucher_service.user_voucher_details(
                identity=identity, user_seller_voucher_id=voucher_id
            )

            if status_code != 200:
                raise ValueError(f"User seller voucher with id: {voucher_id} not found")

            # check and return voucher detail only
            seller_voucher_detail = self.voucher_verification(
                user_voucher_detail=voucher,
                list_seller_id=list_seller_id,
                voucher_list=voucher_list,
                calculated_product_detail=calculated_product_detail,
            )

            calculated_discount = self.calculate_discount(
                calculated_product_detail=calculated_product_detail,
                seller_voucher_detail=seller_voucher_detail,
            )

            seller_id = seller_voucher_detail["seller_id"]

            voucher_list[seller_id] = {
                "total_discount": calculated_discount,
                "user_seller_voucher_id": voucher_id,
            }

        return voucher_list

    def calculate_discount(self, calculated_product_detail, seller_voucher_detail):
        seller_id = seller_voucher_detail["seller_id"]

        total_price = calculated_product_detail[seller_id][
            "total_price_before_shipment"
        ]
        percentage = seller_voucher_detail["percentage"]
        discount_type_name = seller_voucher_detail["discount_type_name"]
        max_discount_amount = seller_voucher_detail["max_discount_amount"]

        if discount_type_name == "PERCENTAGE":
            total_discount = total_price * percentage / 100

            if total_discount > max_discount_amount:
                total_discount = max_discount_amount

        if discount_type_name == "FIXED_DISCOUNT":
            total_discount = max_discount_amount

        return total_discount

    def voucher_verification(
        self,
        user_voucher_detail,
        list_seller_id,
        voucher_list,
        calculated_product_detail,
    ):
        detail = user_voucher_detail["seller_voucher_detail"]

        if user_voucher_detail["is_used"] == 1:
            raise ValueError(
                f"Voucher with id: {user_voucher_detail['id']} has been used"
            )

        if detail["is_active"] == 0:
            raise ValueError("Voucher is not active")

        if detail["usage_limit"] <= 0:
            raise ValueError("Voucher usage limit reached")

        if detail["start_date"] >= datetime.now():
            raise ValueError("Voucher has not started yet")

        if detail["expiry_date"] < datetime.now():
            raise ValueError("Voucher has expired")

        # if voucher seller id not in list items' seller id
        if detail["seller_id"] not in list_seller_id:
            raise ValueError("Used only voucher from purchased items' seller")

        # check if more than 1 voucher per seller is used
        if detail["seller_id"] in voucher_list:
            raise ValueError("Used only 1 voucher per seller")

        if (
            calculated_product_detail[detail["seller_id"]][
                "total_price_before_shipment"
            ]
            < detail["min_purchase_amount"]
        ):
            raise ValueError("Voucher purchase amount not reached")

        return detail
