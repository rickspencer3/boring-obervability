from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.checks import bp
from app.models.checks import Check
from app.models.headers import Header
from app.models.anomaly_detectors import AnomalyDetector
from app.extensions import db
from app import iox_dbapi
from config import Config
import matplotlib.pyplot as plt, mpld3
import matplotlib

from flightsql import FlightSQLClient
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.offline as py

matplotlib.pyplot.switch_backend('Agg') 

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
        header = Header(key = request.form['key'], 
                        value = request.form['value'],
                        check_id = check_id)
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
    bin_divisor = {
        "h": "1.0",
        "d": "10.0",
        "w": "60.0"
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

    fig = px.line(results, x='binned', y='error_rate')
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

    fig = px.line(results, x='binned', y='elapsed', color='id')
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

    fig = px.line(results, x='time', y='elapsed', color='id')
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