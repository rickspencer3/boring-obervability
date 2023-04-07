from app.models.checks import Check
from requests import request
from requests.exceptions import ConnectionError
from app.extensions import db, influxdb_write
from flask import current_app
from datetime import timedelta

def run_checks():
    with db.app.app_context():
        checks = Check.query.filter_by(enabled=True).all()

        for check in checks:
            headers = {}
            name = check.name.replace(" ","\ ")
            for header in check.headers:
                headers[header.key] = header.value
            try:
                check_response = request(method=check.method, 
                                    url=check.url,
                                    data=check.content,
                                    headers=headers)
            except ConnectionError as e:
                # the server is totally down, didn't response at all
                lp = f"""checks,url="{check.url}",name={name},method={check.method},user_id={check.user_id},id={check.id} status=404i,elapsed=0i"""
                response = ConnectionErrorResponse()
                detect_anomolies_and_record(check, response, lp)
                _log_response_error(check, e)
                break
            except Exception as e:
                _log_response_error(check, e)
                break
            
            log_dict = {"check_id":check.id,
                        "check_name":check.name,
                        "anomaly_dectors": len(check.anomaly_detectors),
                        "response_text":check_response.text}
            current_app.logger.info(log_dict)
            lp = f"""checks,url="{check.url}",name={name},method={check.method},user_id={check.user_id},id={check.id} status={check_response.status_code}i,elapsed={check_response.elapsed.microseconds}i"""
            
            detect_anomolies_and_record(check, check_response, lp)

def detect_anomolies_and_record(check, check_response, lp):
    for anomaly_detector in check.anomaly_detectors:
        anomaly_detector.detect(check=check, response=check_response)
    influxdb_write(lp)

def _log_response_error(check, e):
    error_log_dict = {
                    "check_id":check.id,
                    "check_name":check.name,
                    "exception": str(e)
                }
    current_app.logger.error(error_log_dict)

class ConnectionErrorResponse:
    status_code = 404
    elapsed = timedelta()