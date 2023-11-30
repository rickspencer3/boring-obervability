import secrets
import string

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config
from pprint import pprint
from influxdb_client_3 import InfluxDBClient3, SYNCHRONOUS

db = SQLAlchemy()
mail = Mail()

def influxdb_write(point):
    try:
        client = InfluxDBClient3(
            host=Config.INFLUXDB_FLIGHT_HOST,
            org=Config.INFLUXDB_ORG_ID,
            database=Config.INFLUXDB_BUCKET,
            token=Config.INFLUXDB_WRITE_TOKEN,
            write_options=SYNCHRONOUS
        )
        pprint(client.write(record=point.to_line_protocol()))
    except Exception as e:
        print(f"Error writing result to InfluxDB {e}")

def influxdb_query(sql):
    client = InfluxDBClient3(
        host=Config.INFLUXDB_FLIGHT_HOST,
        org=Config.INFLUXDB_ORG_ID,
        database=Config.INFLUXDB_BUCKET,
        token=Config.INFLUXDB_READ_TOKEN
    )
    return client.query(query=sql , language="sql")


def generate_id_string(length=8):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))


