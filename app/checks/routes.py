from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from requests import request as http_request
from html import escape
from flask import current_app
from app.checks.forms import FormTypes
from app.checks import bp
from app.models import CheckClass
from app.models.checks import Check
from app.models.headers import Header
from app.models.anomaly_detectors import AnomalyDetector
from app.extensions import db
from config import Config

from flightsql import FlightSQLClient
import plotly.io as pio
import plotly.express as px

@bp.route('/')
@login_required
def index():
    all_checks = current_user.checks
    return render_template('checks/index.html', checks = all_checks)

@bp.route('<check_id>/add_anomaly_detector', methods = ["GET","POST"])
@login_required
def add_anomaly_detector(check_id):
    if request.method == "GET":
        check = Check.query.get(check_id)
        anomaly_detectors = current_user.anomaly_detectors
        return render_template('checks/add_anomaly_detector.html', 
                                check=check, anomaly_detectors=anomaly_detectors)
    elif request.method == "POST":
        check = Check.query.get(check_id)
        anomaly_detector = AnomalyDetector.query.get(request.form['anomaly_detector_id'])
        check.anomaly_detectors.append(anomaly_detector)
        db.session.add(check)
        db.session.commit()
        return redirect(url_for('checks.details', check_id=check_id))

@bp.route('/<check_id>/headers', methods=["GET","POST"])
@login_required
def add_header(check_id):
    check = Check.query.get(check_id)
    if request.method == "GET":
        headers = current_user.headers
        return render_template('checks/add_header.html', check=check, headers=headers)
    elif request.method == "POST":
        header = Header.query.get(request.form["header_id"])
        check.headers.append(header)
        db.session.add(check)
        db.session.commit()
        return redirect(url_for('checks.details', check_id=check_id))

@bp.route('/<check_id>')
@login_required
def details(check_id):
    check = Check.query.get(check_id)
    type = check.type
    return render_template(f'checks/details_{type}.html', check=check)

@bp.route('/enabled', methods=["POST"])
@login_required
def enabled():
    check_id = request.form.get('check_id')
    enabled = request.form.get('enabled') == 'true'
    check = Check.query.get(check_id)
    if(check.user.id != current_user.id):
        return "", 404
    
    check.enabled = enabled
    db.session.commit()
    return "success", 200

@bp.route('/test', methods=["POST"])
@login_required
def test():
    check_id = request.form.get('check_id')
    check = Check.query.get(check_id)
    if(check.user.id != current_user.id):
        return "", 404
    headers = {}
    for header in check.headers:
        headers[header.key] = header.value
    check_response = http_request(method=check.method, 
                        url=check.url,
                        data=check.content,
                        headers=headers)

    log_dict = {"check_id":check.id,
                "check_name":check.name,
                "anomaly_dectors": len(check.anomaly_detectors),
                "response_text":check_response.text,
                "test":True
                }
    current_app.logger.info(log_dict)
    html = f"""
<div>Test Result</div>
<TABLE>
<TR><TD>response code</TD><TD>{check_response.status_code}</TD></TR>
<TR><TD>response latency (secoonds)</TD><TD>{check_response.elapsed.total_seconds()}</TD></TR>
<TR><TD>response text</TD><TD>{escape(check_response.text)}</TD></TR>
</TABLE>
    """
    return html, 200

@bp.route('/latency_graph/<time_range>', methods=["GET"])
@login_required
def latency_graph(time_range=None):
    if time_range is None or time_range == "h":
        grph = _latency_graph_1h()
        return grph, 200
    elif time_range == "d":
        grph = _latency_graph_aggregated('10 minutes', '1 day')
        return grph, 200
    elif time_range == "w":
        grph = _latency_graph_aggregated('1 hour', '1 week')
        return grph, 200
    elif time_range == "m":
        grph = _latency_graph_aggregated('4 hour', '1 month')
        return grph, 200

@bp.route('/status_graph/<time_range>', methods=["GET"])
@login_required
def status_graph(time_range=None):
    if time_range == None:
        time_range = "h"
    interval = {
        "h": "1 hour",
        "d": "1 day",
        "w": "1 week",
        "m": "1 month"
    }[time_range]
    bin_interval = {
        "h": "1 minute",
        "d": "10 minutes",
        "w": "1 hour",
        "m": "4 hours"
    }[time_range]

    sql = f"""
SELECT
  DATE_BIN(INTERVAL '{bin_interval}', time, '1970-01-01T00:00:00Z'::TIMESTAMP) AS binned,
    check_name,
   SUM(error)::double / COUNT(error)::double  AS error_rate
FROM checks
WHERE time > now() - interval'{interval}'
AND user_id = '{current_user.id}'
AND check_name IS NOT NULL
GROUP BY check_name, binned
ORDER BY check_name, binned
    """

    client = FlightSQLClient(host=Config.INFLUXDB_FLIGHT_HOST,
                        token=Config.INFLUXDB_READ_TOKEN,
                        metadata={'bucket-name': f"{Config.INFLUXDB_BUCKET}"})

    query = client.execute(sql)
    reader = client.do_get(query.endpoints[0].ticket)
    table = reader.read_all()
    results = table.to_pandas()
    results.rename(columns={'binned':'time',"check_name":"Check Name"},inplace=True)

    fig = px.line(results, x='time', y='error_rate', color='Check Name', title=f"Check Error Rates ({bin_interval})")
    return pio.to_html(fig, 
                        config=None, 
                        auto_play=True, 
                        include_plotlyjs=True, 
                        include_mathjax=False, 
                        post_script=None, 
                        full_html=False, 
                        animation_opts=None, 
                        default_width='600px', default_height='500px', 
                        validate=True, 
                        div_id=None), 200




@bp.route('remove_detector', methods=["POST"])
@login_required
def remove_detector():
    check_id = request.form["check_id"]
    check = Check.query.get(check_id)
    if current_user.id != check.user.id:
        return "", 404

    anomaly_detector_id = request.form["anomaly_detector_id"]

    anomaly_detector = AnomalyDetector.query.get(anomaly_detector_id)
    check.anomaly_detectors.remove(anomaly_detector)
    db.session.commit()
    return redirect(url_for('checks.index'))

@bp.route('remove_header', methods=["POST"])
@login_required
def remove_header():
    header_id = request.form["header_id"]
    header = Header.query.get(header_id)
    check_id = request.form["check_id"]
    check = Check.query.get(check_id)

    if current_user.id != header.user_id or current_user.id != check.user.id:
        return "", 404
    else:
        check.headers.remove(header)
        db.session.commit()
        return "",200

@bp.route('<check_id>/edit', methods=["GET","POST"])
@login_required
def edit(check_id):
    check = Check.query.get(check_id)

    if current_user.id is not check.user.id:
        return "", 404
    if request.method == "GET":
        return render_template(f'checks/edit_{check.type}.html',
                    form=check.form_class(obj=check),
                    check=check)
    else:
        form = check.form_class()
        check = Check.query.get(check_id)
        form.id = check_id
        form.process(obj=check)
        form.process(formdata=request.form)
        if form.validate_on_submit():
            form.populate_obj(check)
            check.enabled = 'enabled' in request.form
            db.session.commit()
            
            return redirect(url_for('checks.details', check_id=check.id))
        else:
            return form.errors, 400


@bp.route('<type>/new', methods=["GET", "POST"])
@login_required
def new(type):
    form = FormTypes[type]()
    if request.method == "GET":
        return render_template(f'checks/new_{type}.html', form=form)

    if request.method == "POST":
        form.process(formdata=request.form)
        if form.validate_on_submit():
            new_check = CheckClass[type]()
            form.populate_obj(new_check)
            
            new_check.user_id = current_user.id
            new_check.enabled = True
            new_check.type = type
            db.session.add(new_check)
            db.session.commit()
        
            return redirect(url_for('checks.index'))
        else:
            return form.errors, 400


def _latency_graph_aggregated(interval, time_range_start):
    sql = f"""
SELECT
    date_bin(interval '{interval}', time, TIMESTAMP '2001-01-01 00:00:00Z') as binned,
  avg(latency) latency,
  check_name

FROM checks
WHERE time > now() - INTERVAL '{time_range_start}'
AND user_id = '{current_user.id}'
AND check_name IS NOT NULL
GROUP BY check_name, binned
ORDER BY check_name, binned
    """
 
    client = FlightSQLClient(host=Config.INFLUXDB_FLIGHT_HOST,
                token=Config.INFLUXDB_READ_TOKEN,
                metadata={'bucket-name': f"{Config.INFLUXDB_BUCKET}"})

    query = client.execute(sql)
    reader = client.do_get(query.endpoints[0].ticket)
    table = reader.read_all()
    results = table.to_pandas()
    results.rename(columns={'binned':'time', 'check_name':"Check Name"}, inplace=True)

    fig = px.line(results, x='time', y='latency', color='Check Name', title="Check Latencies Check Latencies (Milliseconds)")
    return pio.to_html(fig, 
                    config=None, 
                    auto_play=True, 
                    include_plotlyjs=True, 
                    include_mathjax=False, 
                    post_script=None, 
                    full_html=False, 
                    animation_opts=None, 
                    default_width='600px', default_height='500px', 
                    validate=True, 
                    div_id=None)

def _latency_graph_1h():
    sql = f"""
select 
    check_name, latency, time  
from checks where  
    time > now() - interval'60 minutes' 
AND user_id = '{current_user.id}'
AND check_name IS NOT NULL
order by 
    check_name, time
    """
    client = FlightSQLClient(host=Config.INFLUXDB_FLIGHT_HOST,
                    token=Config.INFLUXDB_READ_TOKEN,
                    metadata={'bucket-name': f"{Config.INFLUXDB_BUCKET}"})

    query = client.execute(sql)
    reader = client.do_get(query.endpoints[0].ticket)
    table = reader.read_all()
    
    results = table.to_pandas()
    results.rename(columns={'check_name':"Check Name"}, inplace=True)

    fig = px.line(results, x='time', y='latency', color='Check Name', title="Check Latencies (Milliseconds)")
    return pio.to_html(fig, 
                    config=None, 
                    auto_play=True, 
                    include_plotlyjs=True, 
                    include_mathjax=False, 
                    post_script=None, 
                    full_html=False, 
                    animation_opts=None, 
                    default_width='600px', 
                    default_height='500px', 
                    validate=True, 
                    div_id=None)

@bp.route('/delete', methods=["POST"])
@login_required
def delete():
    check_id = request.form["check_id"]
    check = Check.query.get(check_id)
    if current_user.id is not check.user.id:
        return "", 404
    db.session.delete(check)
    db.session.commit()

    return "success", 200