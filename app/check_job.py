from app.models.checks import Check
from requests import request
from requests.exceptions import ConnectionError
from app.extensions import db, influxdb_write
from flask import current_app
from datetime import timedelta

def run_checks():
    with db.app.app_context():
        checks = Check.query.filter_by(enabled=True).all()

        for check in checks:
            check.run()