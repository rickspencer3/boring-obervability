from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.notifications import bp
from app.extensions import db
from app.models.notifications import Notification
from app import iox_dbapi
from config import Config

@bp.route('/')
@login_required
def index():
    notifications = current_user.notifications
    return render_template('notifications/index.html', notifications=notifications)

@bp.route('/<notification_id>')
@login_required
def details(notification_id):
    notification = Notification.query.get(notification_id)
    return render_template('notifications/details.html', notification=notification)

@bp.route('/issues')
@login_required
def issues_table():
    sql = f"select check, type, value, time from detected where user_id = {current_user.id} and time > now() - interval'1 hour'"
    connection = iox_dbapi.connect(
        host = Config.INFLUXDB_HOST,
        org = Config.INFLUXDB_ORG_ID,
        bucket = Config.INFLUXDB_BUCKET,
        token = Config.INFLUXDB_READ_TOKEN)
    cursor = connection.cursor()
    cursor.execute(sql)
    t = "<TABLE><TR><TH>check id</TH><TH>type</TH><TH>value</TH><TH>time</TH><TR>"
    d = cursor.fetchone()
    while d is not None:
        t += f"<TR><TD>{d[2]}</TD><TD>{d[3]}</TD><TD>{d[4]}</TD><TD>{d[5]}</TD></TR>"
        d = cursor.fetchone()
    t += "</TABLE>"

    return t, 200

@bp.route('/new', methods=["GET","POST"])
@login_required
def new():
    if request.method == "GET": 
        notification_channels = current_user.notification_channels
        return render_template('notifications/new.html',
        notification_channels=notification_channels)
    if request.method == "POST":
        new_notification = Notification(
            name=request.form['name'],
            type=request.form['type'],
            value=request.form['value'],
            notification_channel_id = request.form['channel'],
            user_id = current_user.id
        )
        db.session.add(new_notification)
        db.session.commit()
        return redirect(url_for('notifications.index'))