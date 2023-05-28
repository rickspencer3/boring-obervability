from requests import request
from datetime import timedelta

from flask import current_app
from app.extensions import db, influxdb_write
from app.models.checks import Check
from app.models.check_result import CheckResult

class HTTPCheck(Check):
    content = db.Column(db.String(600))
    method = db.Column(db.String(10))
    url = db.Column(db.String(100))

    __mapper_args__ = {
    'polymorphic_identity': 'http',
    }
    
    @property
    def form_class(self):
        import app.checks.forms as forms
        return forms.HTTPForm

    def run(self):
        print(f"run HTTPCheck {self.id}, {self.name}")
        headers = {}
        # name = self.name.replace(" ","\ ")
        for header in self.headers:
            headers[header.key] = header.value
        error_type = ""
        fields = {"method": self.method}
        check_response = None
        try:
            check_response = request(method=self.method, 
                                url=self.url,
                                data=self.content,
                                headers=headers)

            # assuming the request worked, set up the info for the result
            error = 1 if check_response.status_code > 399 else 0
            if check_response.status_code > 499:
                error_type = "server"
            elif check_response.status_code > 399:
                error_type = "client"
            fields["status"] = check_response.status_code
        except Exception as e:
            error = 1
            error_type = "exception"
            fields["exception"] = str(e)

        if error_type != "":
            fields["error_type"] = error_type

        check_result = CheckResult(
                                self,
                                error=error,
                                end_point=self.url,
                                latency = check_response.elapsed.microseconds / 1000 if check_response is not None else None,
                                fields=fields)
        influxdb_write(check_result)

        for detector in self.anomaly_detectors:
            detector.detect(check_result)
        # self.detect_anomolies_and_record(self, check_response, check_result)
        # current_app.logger.info(f'{check_result.to_line_protocol()} at {check_result.time}')

    def detect_anomolies_and_record(self, check, check_response, point):
        for anomaly_detector in check.anomaly_detectors:
            anomaly_detector.detect(check=check, check_result=check_response)
        influxdb_write(point)

    def _log_response_error(self, check, e):
        error_log_dict = {
                        "check_id":check.id,
                        "check_name":check.name,
                        "exception": str(e)
                    }
        current_app.logger.error(error_log_dict)

class ConnectionErrorResponse:
    status_code = 404
    elapsed = timedelta()