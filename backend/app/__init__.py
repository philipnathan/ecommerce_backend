import os
import cloudinary
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flasgger import Swagger
from flask_cors import CORS
from pyngrok import ngrok

from .db import db
from .db import mongo
from .controllers.users import users_blueprint
from .controllers.sellers import sellers_blueprint
from .controllers.locations import locations_blueprint
from .controllers.products import products_blueprint
from .controllers.addresses import addresses_blueprint
from .controllers.seller_vouchers import seller_vouchers_blueprint
from .controllers.user_seller_vouchers import user_seller_vouchers_blueprint
from .controllers.carts import carts_blueprint
from .controllers.shipping_options import shipping_options_blueprint
from .controllers.shipments import shipments_blueprint
from .controllers.calculators import calculators_blueprint
from .controllers.categories import categories_blueprint
from .controllers.transactions import transactions_blueprint

load_dotenv(override=True)
migrate = Migrate()
jwt = JWTManager()

username = os.getenv("MYSQL_USERNAME")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
database = os.getenv("MYSQL_DATABASE")


def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+mysqlconnector://{username}:{password}@{host}/{database}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["MIDTRANS_SERVER_KEY"] = os.getenv("MIDTRANS_SERVER_KEY")
    app.config["MIDTRANS_IS_PRODUCTION"] = os.getenv("MIDTRANS_IS_PRODUCTION")
    app.config["MIDTRANS_CLIENT_KEY"] = os.getenv("MIDTRANS_CLIENT_KEY")

    ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))

    app.register_blueprint(users_blueprint)
    app.register_blueprint(sellers_blueprint)
    app.register_blueprint(locations_blueprint)
    app.register_blueprint(products_blueprint)
    app.register_blueprint(addresses_blueprint)
    app.register_blueprint(seller_vouchers_blueprint)
    app.register_blueprint(user_seller_vouchers_blueprint)
    app.register_blueprint(carts_blueprint)
    app.register_blueprint(shipping_options_blueprint)
    app.register_blueprint(shipments_blueprint)
    app.register_blueprint(calculators_blueprint)
    app.register_blueprint(categories_blueprint)
    app.register_blueprint(transactions_blueprint)

    db.init_app(app)
    mongo.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    Swagger(app)
    CORS(app)

    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    )

    with app.app_context():
        db.create_all()

    return app
