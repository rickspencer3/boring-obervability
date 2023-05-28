from influxdb_client.client.write.point import Point
from time import time_ns

class CheckResult(Point):
    """
    This class represents an Observation, which is a special type of InfluxDB Point.
    Specifically, the result of Check.run(). Used to write results to InfluxDB.
    """
    
    def __init__(self,
                 check=None,
                 error = 0,
                 latency = None,
                 end_point = "",
                 tags={}, 
                 fields={}):
        """
        Create a new Observation.

        :param check: The Check that produced the result. Required.
        :param error: Set to 1 if an error was observed. Defaults to 0.
        :param latency: The latency of the Check, in milliseconds. Optional, but almost always should be set.
        :param end_point: The url or host name that the Check was targeting. Required.
        :param tags: A dictionary of additional tags for the Observation. Optional.
        :param fields: A dictionary of additional fields for the Observation. Optional.
        """
        
        # Guard conditions
        if check == None:
            raise Exception("Check required.")
        if end_point == "":
            raise Exception("Empty end_point not allowed.")
              
        super().__init__("checks")
        self._error = error
        self._check_id = check.id
        self._user_id = check.user.id

        # Add required tags
        self.tag("check_name",f'"{check.name}"')
        self.tag("user_id", check.user.id)
        self.tag("check_id",check.id)
        self.tag("end_point", f'"{end_point}"')


        if latency is not None:
            self.field("latency", latency)

        # Add additional keys and fields (if any)
        for key, value in tags.items():
            self.tag(key,value)

        for key, value in fields.items():
            self.field(key,value)

        # Timestamp with current time
        self.time = time_ns()

    @property 
    def error(self):
        return self._error
    
    @property
    def check_id(self):
        return self._check_id



