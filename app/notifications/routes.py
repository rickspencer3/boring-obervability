from flask import render_template, request
from flask_user import login_required, current_user
from app.notifications import bp
from app.extensions import db

@bp.route('/')
@login_required
def index():
    notifications = current_user.notifications
    return render_template('notifications/index.html', notifications=notifications)

@bp.route('/new', methods=["GET","POST"])
@login_required
def new():
    if request.method == "GET": 
        email_channels = current_user.email_channels
        sms_channels = current_user.email_channels
        return render_template('notifications/new.html',
        email_channels=email_channels, sms_channels=sms_channels)
    if request.method == "POST":
        print(request.form['channels'])
        notifications = current_user.notifications
        return render_template('notifications/index.html', notifications=notifications)