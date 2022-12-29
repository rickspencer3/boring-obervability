from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.notifications import bp
from app.extensions import db
from app.models.notifications import Notification

@bp.route('/')
@login_required
def index():
    notifications = current_user.notifications
    return render_template('notifications/index.html', notifications=notifications)

@bp.route('/<check_id>')
@login_required
def details(notification_id):
    notification = Notification.query.get(notification_id)
    return render_template('notifications/details.html', notification=notification)

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