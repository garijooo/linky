import os

from flask import Flask
from flask_cors import CORS
from flask_redis import FlaskRedis

from config import DevConfig, TestConfig

redis_store = FlaskRedis()


def create_app(config=TestConfig):
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV")
    if env == "development":
        config = DevConfig

    app.config.from_object(config)

    cors = CORS(app)
    cors.init_app(app, resources={"*": {"origins": "*"} })

    redis_store.init_app(app)

    from .views import bp
    app.register_blueprint(bp)

    return app
