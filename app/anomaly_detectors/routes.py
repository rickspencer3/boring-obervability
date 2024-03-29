from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.anomaly_detectors import bp
from app.extensions import db
from app.models.anomaly_detectors import LatencyDetector, ErrorDetector, AnomalyDetector
from app.anomaly_detectors.forms import LatencyDetectorForm, ErrorDetectorForm
from app.models.checks import Check
from app.models.notification_channels import NotificationChannel
from config import Config
from app.anomaly_detectors.forms import AnomalyDetectorForm
from pyarrow.lib import ArrowInvalid
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
    db.session.delete(anomaly_detector)
    db.session.commit()
    return "success", 200


@bp.route('/<anomaly_detector_id>/edit', methods=["GET", "POST"])
@login_required
def edit(anomaly_detector_id):
    anomaly_detector = AnomalyDetector.query.get(anomaly_detector_id)
    
    if current_user.id is not anomaly_detector.user.id:
        return "", 404
    
    if anomaly_detector.type == "error":
        form = ErrorDetectorForm()
    elif anomaly_detector.type == "latency":
        form = LatencyDetectorForm()
    else:
        return "Unknown detector type", 400

    form.process(obj=anomaly_detector)
    
    if request.method == "GET":
        return render_template(f'anomaly_detectors/edit_{anomaly_detector.type}.html',
                               form=form,
                               anomaly_detector=anomaly_detector)
                               
    elif request.method == "POST":
        form.process(formdata=request.form)
        if form.validate_on_submit():
            anomaly_detector.name = request.form['name']
            
            if anomaly_detector.type == "error":
                anomaly_detector.status_lower_bound = request.form['status_lower_bound']
            elif anomaly_detector.type == "latency":
                anomaly_detector.latency_lower_bound = request.form['latency_lower_bound']
                
            db.session.commit()
            return redirect(url_for('anomaly_detectors.details', anomaly_detector_id=anomaly_detector.id))
        else:
            return form.errors, 400

            
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
 
    sql = f"select check, type, value, observed, time from anomalies where user_id = '{current_user.id}' and time > now() - interval'{interval}' order by time desc"
    client = FlightSQLClient(host=Config.INFLUXDB_FLIGHT_HOST,
                        token=Config.INFLUXDB_READ_TOKEN,
                        metadata={'bucket-name': f"{Config.INFLUXDB_BUCKET}"})

    try:
        query = client.execute(sql)
        reader = client.do_get(query.endpoints[0].ticket)
    except ArrowInvalid as e:
        return "No Anomalies Detected"
    table = reader.read_all()
    if table.num_rows == 0:
        return "No Anomalies Detected"
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
                    cells=dict(values=[df.check, df.type, df.value, df.observed, df.time, df['check name']],
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
@bp.route('/new/<detector_type>', methods=["GET", "POST"])
@login_required
def new(detector_type=None):
    if detector_type == "latency":
        form = LatencyDetectorForm()
    elif detector_type == "error":
        form = ErrorDetectorForm()
    else:
        return "Invalid detector type", 400

    if request.method == "GET":
        return render_template(f'anomaly_detectors/new_{detector_type}.html',
                               form=form)
    if request.method == "POST":
        form.process(formdata=request.form)
        if form.validate_on_submit():
            if detector_type == "latency":
                new_anomaly_detector = LatencyDetector(
                    name=request.form['name'],
                    type=detector_type,
                    latency_lower_bound=request.form['latency_lower_bound'],
                    user_id=current_user.id
                )
            elif detector_type == "error":
                new_anomaly_detector = ErrorDetector(
                    name=request.form['name'],
                    type=detector_type,
                    status_lower_bound=request.form['status_lower_bound'],
                    user_id=current_user.id
                )

            db.session.add(new_anomaly_detector)
            db.session.commit()
            return redirect(url_for('anomaly_detectors.index'))
        else:
            return form.errors, 400

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