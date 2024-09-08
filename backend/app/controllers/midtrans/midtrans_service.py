import os
import hashlib
import midtransclient.transactions
import midtransclient
from dotenv import load_dotenv

load_dotenv()


class MidtransService:

    def webhook(self, data):
        received_signature = data["signature_key"]

        if not self.verify_signature_key(data, received_signature):
            return {"error": "Invalid Signature Key"}, 403

        return {"message": "Transaction processed successfully"}, 200

    def create_transaction(self, data, parent_id):
        get_param = self.get_param(data)
        snap = midtransclient.Snap(
            is_production=False,
            server_key=os.getenv("MIDTRANS_SERVER_KEY"),
        )

        param = {
            "transaction_details": {
                "order_id": parent_id,
                "gross_amount": get_param["all_final_price"],
            },
            "item_details": get_param["item_details"],
            "credit_card": {"secure": True},
        }

        snap_response = snap.create_transaction(param)

        return snap_response

    def verify_signature_key(self, data, received_signature):
        order_id = data["order_id"]
        status_code = data["status_code"]
        gross_amount = data["gross_amount"]
        server_key = os.getenv("MIDTRANS_SERVER_KEY")

        payload = order_id + status_code + gross_amount + server_key
        generated_signature = hashlib.sha512(payload.encode("utf-8")).hexdigest()

        return generated_signature == received_signature

    def get_param(self, data):
        all_final_price = 0
        shipment_costs = 0
        total_discount = 0
        item_details = []

        for seller_id, details in data.items():
            all_final_price += details["final_price"]
            shipment_costs += details["shipment_fee"]

            if details.get("total_discount", None):
                total_discount += details["total_discount"]

            for detail in details["items"]:
                item = {
                    "id": detail["detail_product"]["id"],
                    "price": detail["detail_product"]["price"],
                    "quantity": detail["quantity"],
                    "name": detail["detail_product"]["name"],
                }

                item_details.append(item)

        item_details.append(
            {
                "id": "SHIPPING_COST",
                "price": shipment_costs,
                "quantity": 1,
                "name": "SHIPPING_COST",
            }
        )

        if total_discount > 0:
            item_details.append(
                {
                    "id": "DISCOUNT",
                    "price": -total_discount,
                    "quantity": 1,
                    "name": "DISCOUNT",
                }
            )

        return {
            "item_details": item_details,
            "all_final_price": all_final_price,
        }
