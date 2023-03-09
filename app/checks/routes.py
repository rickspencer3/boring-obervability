from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.checks import bp
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

@bp.route('/<check_id>')
@login_required
def details(check_id):
    check = Check.query.get(check_id)
    return render_template('checks/details.html', check=check)

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
def new_header(check_id):
    if request.method == "GET":
        return render_template('headers/new.html')
    elif request.method == "POST":
        header = Header(name = request.form['name'],
                        key = request.form['key'], 
                        value = request.form['value'])
        header.user = current_user
        check = Check.query.get(check_id)
        check.headers.append(header)
        db.session.add(header)
        db.session.commit()
        return redirect(url_for('checks.details', check_id=check_id))

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

@bp.route('/status_graph/<time_range>', methods=["GET"])
@login_required
def status_graph(time_range=None):
    if time_range == None:
        time_range = "h"
    interval = {
        "h": "1 hour",
        "d": "1 day",
        "w": "1 week"
    }[time_range]
    bin_interval = {
        "h": "1 minute",
        "d": "10 minutes",
        "w": "1 hour"
    }[time_range]

    sql = f"""
SELECT
  DATE_BIN(INTERVAL '{bin_interval}', time, '1970-01-01T00:00:00Z'::TIMESTAMP) AS binned,
    id,
   SUM(CASE WHEN status >= 299 THEN 1 ELSE 0 END)::double / COUNT(status)::double  AS error_rate
FROM checks
WHERE time > now() - interval'{interval}'
AND user_id = {current_user.id}
GROUP BY id, binned
ORDER BY id, binned
    """

    client = FlightSQLClient(host=Config.INFLUXDB_FLIGHT_HOST,
                        token=Config.INFLUXDB_READ_TOKEN,
                        metadata={'bucket-name': Config.INFLUXDB_BUCKET})

    query = client.execute(sql)
    reader = client.do_get(query.endpoints[0].ticket)
    table = reader.read_all()
    results = table.to_pandas()
    _add_names_col(results)
    results.rename(columns={'binned':'time'},inplace=True)
    
    fig = px.line(results, x='time', y='error_rate', color='name', title="Check Error Rates")
    return pio.to_html(fig, 
                        config=None, 
                        auto_play=True, 
                        include_plotlyjs=True, 
                        include_mathjax=False, 
                        post_script=None, 
                        full_html=False, 
                        animation_opts=None, 
                        default_width='600px', default_height='300px', 
                        validate=True, 
                        div_id=None), 200

def _add_names_col(df):
    ids = df.id.unique()
    names = {}
    for id in ids:
        names[id] = Check.query.get(id).name
    df['name'] = df['id'].map(names)

@bp.route('/new', methods=["GET","POST"])
@login_required
def new():
    if request.method == "GET":
        return render_template('checks/new.html')

    if request.method == "POST":
        new_check = Check(name = request.form['name'], 
        url = request.form['url'],
        content = request.form['content'],
        method = request.form['method'],
        user_id = current_user.id)
        db.session.add(new_check)
        db.session.commit()
       
        return redirect(url_for('checks.index'))

@bp.route('remove_detector', methods=["POST"])
@login_required
def remove_detector():
    check_id = request.form["check_id"]
    if current_user.id != check.user.id:
        return "", 404

    anomaly_detector_id = request.form["anomaly_detector_id"]
    check = Check.query.get(check_id)

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

@bp.route('<check_id>/edit', methods=["GET", "POST"])
@login_required
def edit(check_id):
    check = Check.query.get(check_id)
    if current_user.id is not check.user.id:
        return "", 404
    if request.method == "GET":
        return render_template('checks/edit.html', check=check)
    elif request.method == "POST":
        check.name = request.form['name']
        check.url = request.form['url']
        check.method = request.form['method']
        check.content = request.form['content']
        db.session.commit()
        
        return redirect(url_for('checks.details', check_id=check.id))

def _latency_graph_aggregated(interval, time_range_start):
    sql = f"""
SELECT
    date_bin(interval '{interval}', time, TIMESTAMP '2001-01-01 00:00:00Z') as binned,
  avg(elapsed) as elapsed,
  id

FROM checks
WHERE time > now() - INTERVAL '{time_range_start}'
AND user_id = {current_user.id}
GROUP BY id, binned
ORDER BY id, binned
    """
 
    client = FlightSQLClient(host=Config.INFLUXDB_FLIGHT_HOST,
                token=Config.INFLUXDB_READ_TOKEN,
                metadata={'bucket-name': Config.INFLUXDB_BUCKET})

    query = client.execute(sql)
    reader = client.do_get(query.endpoints[0].ticket)
    table = reader.read_all()
    results = table.to_pandas()
    _add_names_col(results)
    results.rename(columns={'binned':'time'}, inplace=True)

    fig = px.line(results, x='time', y='elapsed', color='name', title="Check Latencies")
    return pio.to_html(fig, 
                    config=None, 
                    auto_play=True, 
                    include_plotlyjs=True, 
                    include_mathjax=False, 
                    post_script=None, 
                    full_html=False, 
                    animation_opts=None, 
                    default_width='600px', default_height='300px', 
                    validate=True, 
                    div_id=None)

def _latency_graph_1h():
    sql = f"""
select 
    id, elapsed, time 
from checks where  
    time > now() - interval'60 minutes' 
and 
    user_id = {current_user.id}
order by 
    id, time
    """
    client = FlightSQLClient(host=Config.INFLUXDB_FLIGHT_HOST,
                    token=Config.INFLUXDB_READ_TOKEN,
                    metadata={'bucket-name': Config.INFLUXDB_BUCKET})

    query = client.execute(sql)
    reader = client.do_get(query.endpoints[0].ticket)
    table = reader.read_all()
    results = table.to_pandas()
    _add_names_col(results)
    fig = px.line(results, x='time', y='elapsed', color='name', title="Check Latencies")
    return pio.to_html(fig, 
                    config=None, 
                    auto_play=True, 
                    include_plotlyjs=True, 
                    include_mathjax=False, 
                    post_script=None, 
                    full_html=False, 
                    animation_opts=None, 
                    default_width='600px', 
                    default_height='300px', 
                    validate=True, 
                    div_id=None)