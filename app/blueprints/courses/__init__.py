from flask import Blueprint

bp = Blueprint('courses', __name__, url_prefix='/courses', static_folder='static')

from .import models, views