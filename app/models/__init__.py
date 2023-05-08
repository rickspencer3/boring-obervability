from app.models.checks import InfluxDBReadCheck, InfluxDBWriteCheck
from app.models.http_check import HTTPCheck

CheckClass = {"http":HTTPCheck,
                "influxdb_write":InfluxDBWriteCheck,
                "influxdb_read":InfluxDBReadCheck}