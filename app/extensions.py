import secrets
import string

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config

from influxdb_client_3 import InfluxDBClient3, SYNCHRONOUS

db = SQLAlchemy()
mail = Mail()

def influxdb_write(point):
    client = InfluxDBClient3(
        host=Config.INFLUXDB_FLIGHT_HOST,
        org=Config.INFLUXDB_ORG_ID,
        database=Config.INFLUXDB_BUCKET,
        token=Config.INFLUXDB_WRITE_TOKEN,
        write_options=SYNCHRONOUS
    )
    client.write(record=point)

def generate_id_string(length=8):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

influxdb_read_client = InfluxDBClient3(
        host=Config.INFLUXDB_FLIGHT_HOST,
        org=Config.INFLUXDB_ORG_ID,
        database=Config.INFLUXDB_BUCKET,
        token=Config.INFLUXDB_READ_TOKEN
    )
