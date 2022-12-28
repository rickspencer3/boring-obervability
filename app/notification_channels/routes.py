from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.notification_channels import bp
from app.extensions import db

from app.models.notification_channels import SMSChannel, EmailChannel

@bp.route("/")
@login_required
def index():
    email_channels = current_user.email_channels
    sms_channels = current_user.sms_channels
    return render_template('notification_channels/index.html', email_channels=email_channels, sms_channels=sms_channels)

@bp.route('<channel_type>/new', methods=["GET","POST"])
@login_required
def new(channel_type):
    if request.method == "GET":
        if channel_type == "sms":
            return render_template('notification_channels/new_sms.html')
        elif channel_type == "email":
            return render_template('notification_channels/new_email.html')
    elif request.method == "POST":
        if channel_type == "sms":
            chan = SMSChannel(name = request.form['name'],
                number = request.form['number'],
                user_id = current_user.id)
            db.session.add(chan)
            db.session.commit()
        elif channel_type == "email":
            chan=EmailChannel(name=request.form['name'],
            address=request.form['address'],
            user_id = current_user.id)
            db.session.add(chan)
            db.session.commit()
        return redirect(url_for('notification_channels.index'))

    
