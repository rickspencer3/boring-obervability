import secrets
import string

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from requests import post
from config import Config
from flask import current_app

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

db = SQLAlchemy()
mail = Mail()

def influxdb_write(point):
    client = InfluxDBClient(url=Config.INFLUXDB_HOST, token=Config.INFLUXDB_WRITE_TOKEN)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=Config.INFLUXDB_BUCKET, 
                    org=Config.INFLUXDB_ORG_ID,
                    record=point)


def generate_id_string(length=8):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))


