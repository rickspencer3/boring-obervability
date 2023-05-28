from influxdb_client.client.write.point import Point
from app.models.check_result import CheckResult
from time import time_ns

class Anomaly(Point):
    """
    This class represents an Observation, which is a special type of InfluxDB Point.
    Specifically, the result of Check.run(). Used to write results to InfluxDB.
    """
    
    def __init__(self, check, anomaly_detector, fields=[], tags=[]):
        super().__init__("anomalies")
        # lp = f"anomalies,check={check.id},type={self.type},user_id={self.user_id},
        # id={self.id} status_bound={self.status_lower_bound},observed={response.status_code}"
        self.tag("check_id",check.id)
        self.tag("detector_type",anomaly_detector.type)
        self.tag("user_id",anomaly_detector.user.id)
        self.tag("detector_id",anomaly_detector.id)
        self.field("error",anomaly_detector.error)
        self.time = time_ns()

if __name__ == "__main__":
    tags = {"name":"foo_name", "user_id":"foo_user_id","id":"foo_id"}
    fields = {"error":0,"latency":0}
    observation = CheckResult(
                            measurement="foo_measurement",
                            check_name="foo_name",
                            user_id="foo_user_id",
                            check_id="foo_check_id",
                            latency=1000
                            )
    print(observation.to_line_protocol())
