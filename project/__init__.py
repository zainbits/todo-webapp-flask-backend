from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from project import routes
from project.config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    from project.todo.routes import todo
    from project.user.routes import user

    app.register_blueprint(user)
    app.register_blueprint(todo)

    return app
