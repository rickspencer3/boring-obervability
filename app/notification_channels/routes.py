from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.notification_channels import bp
from app.extensions import db

from app.models.notification_channels import NotificationChannel

@bp.route("/")
@login_required
def index():
    notification_channels = current_user.notification_channels
    return render_template('notification_channels/index.html', notification_channels=notification_channels)

@bp.route('/toggle_enabled', methods=["POST"])
@login_required
def set_enabled():
    channel_id = request.form.get('channel')
    enabled = request.form.get('enabled') == 'true'
    channel = NotificationChannel.query.get(channel_id)
    
    channel.enabled = enabled
    db.session.commit()
    return "success", 200

@bp.route('/new', methods=["GET","POST"])
@login_required
def new():
    if request.method == "GET":
        return render_template('notification_channels/new.html')
    if request.method == "POST":
        new_channel = NotificationChannel(
            name=request.form['name'],
            type=request.form['type'],
            value=request.form['value'],
            user_id = current_user.id
        )
        db.session.add(new_channel)
        db.session.commit()
        return redirect(url_for('notification_channels.index'))

    
