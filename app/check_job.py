from app.models.checks import Check
from requests import request
from app.extensions import db, influxdb_write
from app.notify import notify

def run_checks(check_id):
    with db.app.app_context():
        check = Check.query.get(check_id)
        headers = {}
        for header in check.headers:
            headers[header.key] = header.value
        check_response = request(method=check.method, 
                            url=check.url,
                            data=check.content,
                            headers=headers)

        log_dict = {"check_id":check_id,
                    "check_name":check.name,
                    "anomaly_dectors": len(check.anomaly_detectors),
                    "response_text":check_response.text}
        db.app.logger.info(log_dict)

        for anomaly_detector in check.anomaly_detectors:
            notify(anomaly_detector, check, check_response)

        name = check.name.replace(" ","\ ")
        lp = f"""checks,url="{check.url}",name={name},method={check.method},user_id={check.user_id},id={check.id} status={check_response.status_code}i,elapsed={check_response.elapsed.microseconds}i"""
        
        influxdb_write(lp)