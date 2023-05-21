from influxdb_client.client.write.point import Point
from time import time_ns

class Observation(Point):
    """
    This class represents an Observation, which is a special type of InfluxDB Point,
    specifically, the result of Check.run(). Used to write results to InfluxDB.
    """
    
    def __init__(self, 
                 measurement = "",
                 check_name = "",
                 user_id = "",
                 check_id = "",
                 error = 0,
                 error_type = None,
                 latency = None,
                 tags={}, 
                 fields={}):
        """
        Create a new Observation.

        :param measurement: The name of the measurement (aka Table).
        :param check_name: The name of the Check.
        :param user_id: The user_id for the Check.
        :param check_id: The id tag of the Check.
        :param error: Set to 1 if an error was observed. Defaults to 0.
        :param error_type: The error_type field of the Observation. Optional. Should be "client" or "server".
        :param latency: The latency of the Check, in milliseconds. Optional, but almost always should be set.
        :param tags: A dictionary of additional tags for the Observation. Optional.
        :param fields: A dictionary of additional fields for the Observation. Optional.
        """
        
        # Guard conditions
        if measurement == "":
            raise Exception("Empty measurement name not allowed.")
        if check_name == "":
            raise Exception("Empty name not allowed.")
        if user_id == "":
            raise Exception("Empty user_id not allowed.")
        if id == "":
            raise Exception("Empty check_id not allowed.")
        
        super().__init__(measurement)

        # Add required tags
        self.tag("name",check_name)
        self.tag("user_id", user_id)
        self.tag("check_id",check_id)

        # Add fields
        self.field("error", error)
        if error_type is not None:
            if error_type not in ["server","client"]:
                raise Exception(""" 'server' and 'client' are the only valid error types """)
            else:
                self.field("error_type", error_type)
        if latency is not None:
            self.field("latency", latency)

        # Add additional keys and fields (if any)
        for key, value in tags.items():
            self.tag(key,value)
        for key, value in fields.items():
            self.field(key,value)

        # Timestamp with current time
        self.time = time_ns()
        

if __name__ == "__main__":
    tags = {"name":"foo_name", "user_id":"foo_user_id","id":"foo_id"}
    fields = {"error":0,"latency":0}
    observation = Observation(
                            measurement="foo_measurement",
                            check_name="foo_name",
                            user_id="foo_user_id",
                            check_id="foo_check_id",
                            latency=1000
                            )
    print(observation.to_line_protocol())
