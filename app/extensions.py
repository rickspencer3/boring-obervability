from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from requests import post
from config import Config

db = SQLAlchemy()
mail = Mail()

def influxdb_write(lp):
    from flask import current_app
    log_url = f"{Config.INFLUXDB_HOST}api/v2/write?bucket={Config.INFLUXDB_BUCKET}&orgID={Config.INFLUXDB_ORG_ID}"
    log_headers = {"Authorization":f"Token {Config.INFLUXDB_WRITE_TOKEN}"}
    log_response = post(log_url, headers=log_headers, data=lp)
    if log_response.status_code > 299:
        print(f"logging failed with {log_response.status_code}")
        current_app.logger.error(log_response.text)

