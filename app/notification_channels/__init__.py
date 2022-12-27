from flask import Blueprint

bp = Blueprint('notification_channels', __name__)

from app.notification_channels import routes