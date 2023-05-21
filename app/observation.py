from influxdb_client.client.write.point import Point
from time import time_ns
class Observation(Point):
    def __init__(self, 
                 measurement = "",
                 name = "",
                 user_id = "",
                 check_id = "",
                 error = 0,
                 error_type = None,
                 latency = None,
                 tags={}, 
                 fields={}):
        # gaurd conditions
        if measurement == "":
            raise Exception("empty measurement name not allowed")
        if name == "":
            raise Exception("empty name not allowed")
        if user_id == "":
            raise Exception("empty user_id not allowed")
        if id == "":
            raise Exception("empty check_id not allowed")
        
        super().__init__(measurement)

        # add required tags
        self.tag("name",name)
        self.tag("user_id", user_id)
        self.tag("check_id",check_id)

        # add fields
        self.field("error", error)
        if error_type is not None:
            self.field("error_type", error_type)
        if latency is not None:
            self.field("latency", latency)

        # add additional keys and fields (if any)
        for key, value in tags:
            self.tag(key,value)
        for key, value in fields:
            self.field(key,value)

        #time stamp with current time
        self.time = time_ns()
# """checks,url="{self.url}",
# name={name},
# method={self.method},
# user_id={self.user_id},
# id={self.id} 
# 
# status={check_response.status_code}i,
# error={error}i,
# elapsed={check_response.elapsed.microseconds}i"""
        
if __name__ == "__main__":
    tags = {"name":"foo_name", "user_id":"foo_user_id","id":"foo_id"}
    fields = {"error":0,"latency":0}
    observation = Observation(
                            measurement="foo_measurement",
                            name="foo_name",
                            user_id="foo_user_id",
                            check_id="foo_check_id",
                            latency=1000
                            )
    print(observation.to_line_protocol())