from influxdb_client.client.write.point import Point
from app.models.check_result import CheckResult
from time import time_ns

class Anomaly(Point):
    """
    This class represents an Observation, which is a special type of InfluxDB Point.
    Specifically, the result of Check.run(). Used to write results to InfluxDB.
    """
    
    def __init__(self, check_result, anomaly_detector, fields={}, tags={}):
        super().__init__("anomalies")
        self.tag("check_id",check_result.check_id)
        self.tag("check_name", check_result.check_name)
        self.tag("detector_type",anomaly_detector.type)
        self.tag("user_id",anomaly_detector.user.id)
        self.tag("detector_id",anomaly_detector.id)
        self.field("error",check_result.error)
        self.time = time_ns()

        for key, value in fields.items():
            self.field(key, value)
        for key,value in fields.items():
            self.tag(key, value)


