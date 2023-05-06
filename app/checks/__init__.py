from flask import Blueprint

bp = Blueprint('checks', __name__)

from app.checks import routes, http_check_routes