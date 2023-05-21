from requests import request
from datetime import timedelta

from flask import current_app

from app.extensions import db, influxdb_write
from app.models.checks import Check
from app.observation import Observation

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
        try:
            check_response = request(method=self.method, 
                                url=self.url,
                                data=self.content,
                                headers=headers)
        except ConnectionError as e:
            # the server is totally down, didn't response at all
            lp = f"""checks,url="{self.url}",name={self.name},method={self.method},user_id={self.user_id},id={self.id} status=404i,elapsed=0i"""
            response = ConnectionErrorResponse()
            self.detect_anomolies_and_record(self, response, lp)
            self._log_response_error(self, e)
            return
        except Exception as e:
            self._log_response_error(self, e)
            return
        
        log_dict = {"check_id":self.id,
                    "check_name":self.name,
                    "anomaly_dectors": len(self.anomaly_detectors),
                    "response_text":check_response.text}
        current_app.logger.info(log_dict)
        error = 1 if check_response.status_code > 399 else 0
        observation = Observation(measurement="checks",
                                end_point=self.url,
                                check_name=self.name,
                                user_id=self.user_id,
                                check_id=self.id,
                                error=error,
                                latency= check_response.elapsed.microseconds / 1000,
                                  fields={"method":self.method,
                                          "status":check_response.status_code
                                          })
        print("**************")
        print(observation.to_line_protocol())
      
        self.detect_anomolies_and_record(self, check_response, observation)

    def detect_anomolies_and_record(self, check, check_response, point):
        for anomaly_detector in check.anomaly_detectors:
            anomaly_detector.detect(check=check, response=check_response)
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