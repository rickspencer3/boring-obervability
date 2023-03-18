from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.anomaly_detectors import bp
from app.extensions import db
from app.models.anomaly_detectors import AnomalyDetector
from app.models.checks import Check
from app.models.notification_channels import NotificationChannel
from config import Config


from flightsql import FlightSQLClient
import plotly.graph_objects as go
import plotly.io as pio

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


@bp.route('delete', methods=["POST"])
@login_required
def delete():
    anomaly_detector = AnomalyDetector.query.get(request.form["anomaly_detector_id"])
    if anomaly_detector.user.id != current_user.id:
        return "", 404
    if anomaly_detector.user_id == current_user.id:
        db.session.delete(anomaly_detector)
        db.session.commit()
    return "success", 200


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
        db.session.commit()
        return redirect(url_for('anomaly_detectors.details', anomaly_detector_id=anomaly_detector.id))

@bp.route('/issues/<time_range>')
@login_required
def issues_table(time_range=None):
    if time_range == None:
        time_range = "h"
    interval = {
        "h": "1 hour",
        "d": "1 day",
        "w": "1 week",
        "m": "1 month"
    }[time_range]
    sql = f"select check, type, value, time from anomalies where user_id = {current_user.id} and time > now() - interval'{interval}' order by time desc"
    client = FlightSQLClient(host=Config.INFLUXDB_FLIGHT_HOST,
                        token=Config.INFLUXDB_READ_TOKEN,
                        metadata={'bucket-name': Config.INFLUXDB_BUCKET})

    query = client.execute(sql)
    reader = client.do_get(query.endpoints[0].ticket)
    table = reader.read_all()
    df = table.to_pandas()
    
    ids = df.check.unique()
    names = {}
    for id in ids:
        names[id] = Check.query.get(id).name
    df['check name'] = df.check.map(names)


    fig = go.Figure(
                layout={
                    "title":"Anomalies Detected"
                },
                data=[go.Table(
                    columnwidth=[10,20,20,50],
                    header=dict(values=list(df.columns),
                    align='left'),
                    cells=dict(values=[df.check, df.type, df.value, df.time, df['check name']],
                    align='left'),)
                ])
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
                        div_id=None )

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
            user_id=current_user.id
        )
        if request.form["channel"] is not None:
            channel = NotificationChannel.query.get(request.form["channel"])
            new_anomaly_detector.notification_channels.append(channel)
        db.session.add(new_anomaly_detector)
        db.session.commit()
        return redirect(url_for('anomaly_detectors.index'))

@bp.route('/<anomaly_detector_id>/notification_channels', methods=["GET","POST"])
@login_required
def add_notification_channel(anomaly_detector_id):
    anomaly_detector = AnomalyDetector.query.get(anomaly_detector_id)
    if anomaly_detector.user.id != current_user.id:
        return "", 404

    if request.method == "GET":
        channels = current_user.notification_channels
        return render_template('anomaly_detectors/add_notification_channel.html', anomaly_detector=anomaly_detector, channels=channels)
    elif request.method == "POST":
        notification_channel = NotificationChannel.query.get(request.form["channel_id"])
        if notification_channel.user.id != current_user.id:
            return "",404
        anomaly_detector.notification_channels.append(notification_channel)
        db.session.add(anomaly_detector)
        db.session.commit()
        return redirect(url_for('anomaly_detectors.details', anomaly_detector_id=anomaly_detector.id))

@bp.route('remove_notification_channel', methods=["POST"])
@login_required
def remove_notification_channel():
    anomaly_detector = AnomalyDetector.query.get(request.form["anomaly_detector_id"])
    notification_channel = NotificationChannel.query.get(request.form["notification_channel_id"])

    if anomaly_detector.user_id != current_user.id:
        return "", 404

    anomaly_detector.notification_channels.remove(notification_channel)
    db.session.commit()
    return "",200