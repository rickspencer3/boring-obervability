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

@bp.route('/graph', methods=["GET"])
@login_required
def graph():
    check_id = request.args.get('check_id')
    sql = f"select status, elapsed, time from check where  time > now() - interval'60 minutes' and  id = {check_id} order by time"
    
    connection = iox_dbapi.connect(
                    host = Config.INFLUXDB_HOST,
                    org = Config.INFLUXDB_ORG_ID,
                    bucket = Config.INFLUXDB_BUCKET,
                    token = Config.INFLUXDB_READ_TOKEN)
    cursor = connection.cursor()
    cursor.execute(sql)

    fig = plt.figure()
    times = []
    millis = []
    response_codes = []

    result = cursor.fetchone()
    while result != None:
        response_codes.append(result[2])
        millis.append(result[3] / 1000)
        times.append(result[4])

        result = cursor.fetchone()
    plt.plot(times, millis, label = "millisecond latency")
    plt.plot(times, response_codes, label="response codes")
    plt.legend()
    grph = mpld3.fig_to_html(fig)

    return grph, 200

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