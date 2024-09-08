import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from ..users.users_services import UserServices
from ..sellers.sellers_service import SellersServices
from ..addresses.addresses_service import AddressesService
from ..shipping_options.shipping_options_service import ShippingOptionsService


load_dotenv()


class ShipmentService:
    def __init__(
        self,
        user_service=None,
        seller_service=None,
        address_service=None,
        shipping_options_service=None,
    ):
        self.shipping_options_service = (
            shipping_options_service or ShippingOptionsService()
        )
        self.seller_service = seller_service or SellersServices()
        self.user_service = user_service or UserServices()
        self.address_service = address_service or AddressesService()

    def shipment_option_price(self, data, identity):
        """
        { "seller_id" : 2,
          "user_selected_address_id" : 2,
          "total_weight" : 2}
        """

        try:
            seller_id = data.get("seller_id")
            user_selected_address_id = data.get("user_selected_address_id")
            total_weight = data.get("total_weight_gram")

            self.check_user(identity)
            self.check_seller(seller_id)

            user_district = self.check_selected_user_address(
                identity=identity, user_address_id=user_selected_address_id
            )["district_id"]
            seller_district = self.get_seller_address(seller_id=seller_id)[
                "district_id"
            ]

            seller_identity = {"role": "seller", "id": seller_id}
            couriers_option, status_code = (
                self.shipping_options_service.get_option_list(identity=seller_identity)
            )
            if status_code != 200:
                raise ValueError(couriers_option["error"])

            courier = []
            for option in couriers_option:
                if option["is_active"] == 1:
                    courier.append(option["shipment"])

            if len(courier) == 0:
                raise ValueError("Seller does not have any shopping options")

            all_options = asyncio.run(
                self.get_possible_shipment_option(
                    user_district=user_district,
                    seller_district=seller_district,
                    total_weight=total_weight,
                    courier=courier,
                )
            )

            return all_options

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def check_selected_user_address(self, identity, user_address_id):
        address, status_code = self.address_service.get_address_by_id(
            identity=identity, address_id=user_address_id
        )

        if status_code != 200:
            raise ValueError("Address not found")

        return address

    def check_user(self, identity):
        user_id = identity.get("id")
        role = identity.get("role")

        if role != "user":
            raise ValueError("Unauthorized")

        user, status_code = self.user_service.user_info(user_id=user_id)

        if status_code != 200:
            raise ValueError("User not found")

    def check_seller(self, seller_id):
        seller, status_code = self.seller_service.seller_info(seller_id=seller_id)

        if status_code != 200:
            raise ValueError("Seller not found")

    def get_seller_address(self, seller_id):
        identity = {"role": "seller", "id": seller_id}
        address, status_code = self.address_service.list_address(identity=identity)

        if status_code != 200:
            raise ValueError("Seller address not found")

        return address[0]

    async def fetch_courier_options(self, session, link, params, courier):
        params["courier"] = courier
        async with session.post(link, data=params) as response:
            if response.status != 200:
                response_data = await response.json()
                description = response_data["rajaongkir"]["status"]["description"]
                raise Exception(description)

            data = await response.json()
            return data.get("rajaongkir").get("results")[0].get("costs")

    async def get_possible_shipment_option(
        self, user_district, seller_district, total_weight, courier=None
    ):
        link = os.getenv("RAJAONGKIR_LINK")
        key = os.getenv("RAJAONGKIR_KEY")

        if isinstance(courier, list):
            courier = courier
        if isinstance(courier, str):
            courier = [courier]

        available_courier = courier if courier else ["pos", "jne", "tiki"]
        params = {
            "key": key,
            "origin": user_district,
            "destination": seller_district,
            "weight": total_weight,
        }

        all_options = {}

        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_courier_options(session, link, params, each_courier)
                for each_courier in available_courier
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for courier, result in zip(available_courier, results):
                if isinstance(result, Exception):
                    raise Exception(f"Error fetching options for {courier}: {result}")
                else:
                    all_options[courier] = [
                        {
                            "service": option["service"],
                            "cost": option["cost"][0]["value"],
                            "etd": option["cost"][0]["etd"],
                            "description": option["description"],
                        }
                        for option in result
                    ]

        return all_options
