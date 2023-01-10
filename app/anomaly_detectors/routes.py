from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.anomaly_detectors import bp
from app.extensions import db
from app.models.anomaly_detectors import AnomalyDetector
from app.models.checks import Check
from app import iox_dbapi
from config import Config

@bp.route('/')
@login_required
def index():
    anomaly_detectors = current_user.anomaly_detectors
    return render_template('anomaly_detectors/index.html', anomaly_detectors=anomaly_detectors)


@bp.route('/<anomaly_detector_id>', methods=["GET"])
@login_required
def details(anomaly_detector_id):
    if request.method == "GET":
        anomaly_detector = AnomalyDetector.query.get(anomaly_detector_id)
        return render_template('anomaly_detectors/details.html', anomaly_detector=anomaly_detector)


@bp.route('/<anomaly_detector_id>/delete', methods=["POST"])
@login_required
def delete(anomaly_detector_id):
    anomaly_detector = AnomalyDetector.query.get(anomaly_detector_id)
    if anomaly_detector.user_id == current_user.id:
        db.session.delete(anomaly_detector)
        db.session.commit()
    return redirect(url_for('anomaly_detectors.index'))


@bp.route('<anomaly_detector_id>/edit', methods=["GET", "POST"])
@login_required
def edit(anomaly_detector_id):
    anomaly_detector = AnomalyDetector.query.get(anomaly_detector_id)
    if current_user.id is not anomaly_detector.user.id:
        return "", 404
    if request.method == "GET":
        return render_template('anomaly_detectors/edit.html', anomaly_detector=anomaly_detector)
    elif request.method == "POST":
        anomaly_detector.name = request.form['name']
        anomaly_detector.value = request.form['value']
        anomaly_detector.type = request.form['type']
        anomaly_detector.notification_channel_id = request.form['channel']
        db.session.commit()
        return redirect(url_for('anomaly_detectors.details', anomaly_detector_id=anomaly_detector_id))

@bp.route('/issues/<time_range>')
@login_required
def issues_table(time_range=None):
    if time_range == None:
        time_range = "h"
    interval = {
        "h": "1 hour",
        "d": "1 day",
        "w": "1 week"
    }[time_range]
    sql = f"select check, type, value, time from anomalies where user_id = {current_user.id} and time > now() - interval'{interval}' order by time desc"
    connection = iox_dbapi.connect(
        host=Config.INFLUXDB_HOST,
        org=Config.INFLUXDB_ORG_ID,
        bucket=Config.INFLUXDB_BUCKET,
        token=Config.INFLUXDB_READ_TOKEN)
    cursor = connection.cursor()
    cursor.execute(sql)
    t = "<TABLE><TR><TH>check name</TH><TH>check id</TH><TH>type</TH><TH>value</TH><TH>time</TH><TR>"
    d = cursor.fetchone()
    row_count = 0
    while d is not None:
        row_count += 1
        check = Check.query.get(d[2])
        t += f"<TR><TD>{check.name}</TD><TD>{d[2]}</TD><TD>{d[3]}</TD><TD>{d[4]}</TD><TD>{d[5]}</TD></TR>"
        d = cursor.fetchone()
    t += "</TABLE>"

    if row_count == 0:
        return "no anomaliles detected"
    else:
        return t, 200


@bp.route('/new', methods=["GET", "POST"])
@login_required
def new():
    if request.method == "GET":
        notification_channels = current_user.notification_channels
        return render_template('anomaly_detectors/new.html',
                               notification_channels=notification_channels)
    if request.method == "POST":
        new_anomaly_detector = AnomalyDetector(
            name=request.form['name'],
            type=request.form['type'],
            value=request.form['value'],
            notification_channel_id=request.form['channel'],
            user_id=current_user.id
        )
        db.session.add(new_anomaly_detector)
        db.session.commit()
        return redirect(url_for('anomaly_detectors.index'))
