from flask import Flask, jsonify, request
from announcements.config import Config
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
import logging

app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine('postgresql://:@localhost:5432/flask_db')

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager()

docs = FlaskApiSpec()

app.config.update(
    {'APISPEC_SPEC': APISpec(
        title='announcements',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
        'APISPEC_SWAGGER_URL': '/swagger/'
    }
)

from announcements.models import *

Base.metadata.create_all(bind=engine)


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
    )
    file_handler = logging.FileHandler('log/api.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


logger = setup_logger()


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


from announcements.main.views import ads
from announcements.users.views import users

app.register_blueprint(ads)
app.register_blueprint(users)

docs.init_app(app)
jwt.init_app(app)
