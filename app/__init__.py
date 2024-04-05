from flask import Flask
from flask_cors import CORS
from redis import Redis

from config import DevConfig

redis = Redis(host="redis", port=6379)

def create_app(config=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    cors = CORS(app)
    cors.init_app(app, resources={"*": {"origins": "*"} })

    from .views import bp
    app.register_blueprint(bp)

    return app
