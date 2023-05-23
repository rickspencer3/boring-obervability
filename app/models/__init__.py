from app.models.influxdb_write_check import InfluxDBWriteCheck
from app.models.http_check import HTTPCheck
from app.models.influxdb_read_check import InfluxDBReadCheck

CheckClass = {"http":HTTPCheck,
                "influxdb_write":InfluxDBWriteCheck,
                "influxdb_read":InfluxDBReadCheck}