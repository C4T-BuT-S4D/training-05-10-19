from logging.handlers import RotatingFileHandler
import os
import logging
from flask import Flask
from pony import orm

app = Flask(__name__)

app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), app.config['UPLOAD_FOLDER'])
handler = RotatingFileHandler(app.static_folder + '/log.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

db = orm.Database()
db.bind('sqlite', app.config['DB_FILE'], create_db=True)

from app.models import *

db.generate_mapping(create_tables=True)

from app.auth import loggedin

app.jinja_env.globals['logged_in'] = loggedin

from app.views import *
