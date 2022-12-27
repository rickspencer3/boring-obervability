from app.models.checks import Check
from requests import request, post
from app.extensions import db
from config import Config

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

        name = check.name.replace(" ","\ ")
        lp = f"""check,url="{check.url}",name={name},method={check.method},user_id={check.user_id},id={check.id} status={check_response.status_code}i,elapsed={check_response.elapsed.microseconds}i"""
        
        log_url = f"{Config.INFLUXDB_HOST}api/v2/write?bucket={Config.INFLUXDB_BUCKET}&orgID={Config.INFLUXDB_ORG_ID}"
        log_headers = {"Authorization":f"Token {Config.INFLUXDB_WRITE_TOKEN}"}
        log_response = post(log_url, headers=log_headers, data=lp)
        if log_response.status_code > 299:
            print(f"logging failed with {log_response.status_code}")
            print(log_response.text)