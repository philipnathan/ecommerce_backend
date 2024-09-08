from . import categories_blueprint
from .categories_service import CategoriesService
from flasgger import swag_from


service = CategoriesService()


@categories_blueprint.route("/", methods=["GET"])
@swag_from("./categories_get_all.yml")
def get_categories():
    return service.get_categories()
