from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from requests import post
from config import Config
from flask import current_app

db = SQLAlchemy()
mail = Mail()

def influxdb_write(lp):
    log_url = f"{Config.INFLUXDB_HOST}api/v2/write?bucket={Config.INFLUXDB_BUCKET}&org={Config.INFLUXDB_ORG_ID}"
    log_headers = {"Authorization":f"Token {Config.INFLUXDB_WRITE_TOKEN}"}
    log_response = post(log_url, headers=log_headers, data=lp)
    log_dict = {"line_protocol":lp}
    current_app.logger.info(log_dict)
    if log_response.status_code > 299:
        print(f"logging failed with {log_response.status_code}")
        error_dict = {"response_code":log_response.status_code,
                      "response_text":log_response.text,
                      "line_protocol":lp}
        current_app.logger.error(error_dict)

