""" This is Flask HTTP REST API skeleton tempalate that already has the SQL and Elastic databases implemented
Application features:
    python 3.10
    Flask
    MySQL Socket

This module contains the factory function 'create_app' that is responsibility for initializing
the application according to a previous configuration.
"""

from . import urls as api
from .models import *
from flask import Flask
from core import (
    cors,
    jwt,
)
from core.database import *
from core.seeder import init_cli
import os


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', None)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    
    cors.init(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init(app)
    api.init(app)
    init_cli(app)

    return app

from src import models