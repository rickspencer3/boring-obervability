from flask import Blueprint

bp = Blueprint('anomaly_detectors', __name__)

from app.anomaly_detectors import routes