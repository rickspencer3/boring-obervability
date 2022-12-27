from flask import Blueprint

bp = Blueprint('headers', __name__)

from app.headers import routes