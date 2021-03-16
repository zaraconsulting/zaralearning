from flask import Blueprint

bp = Blueprint('main', __name__, url_prefix='/', template_folder='templates')

from .import models, views