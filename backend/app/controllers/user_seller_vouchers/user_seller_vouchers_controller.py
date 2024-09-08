from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from flask import request

from .user_seller_vouchers_service import UserSellerVouchersService
from . import user_seller_vouchers_blueprint

service = UserSellerVouchersService()


@user_seller_vouchers_blueprint.route("/save/<int:seller_voucher_id>", methods=["POST"])
@jwt_required()
@swag_from("./user_seller_vouchers_save.yml")
def user_save_voucher(seller_voucher_id):
    identity = get_jwt_identity()
    return service.user_save_voucher(
        identity=identity, seller_voucher_id=seller_voucher_id
    )


@user_seller_vouchers_blueprint.route("/list", methods=["GET"])
@jwt_required()
@swag_from("./user_seller_vouchers_get_list.yml")
def user_list_vouchers():
    req = request
    identity = get_jwt_identity()
    return service.user_list_vouchers(identity=identity, req=req)


@user_seller_vouchers_blueprint.route(
    "/used/<int:user_seller_voucher_id>", methods=["PUT"]
)
@jwt_required()
@swag_from("./user_seller_vouchers_used.yml")
def user_used_voucher(user_seller_voucher_id):
    identity = get_jwt_identity()
    return service.user_used_voucher(
        identity=identity, user_seller_voucher_id=user_seller_voucher_id
    )
