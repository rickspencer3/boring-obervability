from datetime import timedelta
from flask import current_app
from app.extensions import db, influxdb_write
from app.models.checks import InfluxDBCheck
from app.check_result import CheckResult
from influxdb_client_3 import InfluxDBClient3
import time
from app.extensions import influxdb_write

class InfluxDBReadCheck(InfluxDBCheck):
    sql = db.Column(db.String(300))
    latency = 0
    def run(self):
        error = 0
        try:
            print(f"run InfluxDBReadCheck {self.id}, {self.name}")
            client = InfluxDBClient3(
                token=self.token,
                host=self.host,
                database=self.database,
                org=self.org
            )
            t1 = time.perf_counter()
            client.query(self.sql, language="sql")
            t2 = time.perf_counter()
            
            latency = (t2 - t1) * 1000
        except Exception as e:
            error = 1
    
        observation = CheckResult(
            check_name=self.name,
            user_id=self.user_id,
            check_id=self.id,
            end_point=self.host,
            error=error,
            latency=latency)
        influxdb_write(observation)
        

    @property
    def form_class(self):
        import app.checks.forms as forms
        return forms.InfluxDBReadForm
    
    __mapper_args__ = {
    'polymorphic_identity': 'influxdb_read',
    }