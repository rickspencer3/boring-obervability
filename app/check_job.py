from app.models.checks import Check
from requests import request
from app.extensions import db

def run_checks(check_id):
    with db.app.app_context():
        check = Check.query.get(check_id)
        headers = {}
        for header in check.headers:
            headers[header.key] = header.value
        response = request(method=check.method, 
                            url=check.url,
                            data=check.content,
                            headers=headers)
        print(response.status_code)
    