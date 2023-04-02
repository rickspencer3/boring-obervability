from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.notification_channels import bp
from app.extensions import db

from app.models.notification_channels import NotificationChannel, EmailChannel
from app.notification_channels.forms import EmailChannelForm

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

@bp.route('/new/<channel_type>', methods=["GET", "POST"])
@login_required
def new(channel_type):
    if channel_type == 'email':
        form = EmailChannelForm()
    else:
        return "Invalid channel type", 400

    if request.method == "GET":
        return render_template(f'notification_channels/new_{channel_type}.html', form=form)

    if request.method == "POST":
        form.process(formdata=request.form)
        if form.validate_on_submit():
            if channel_type == 'email':
                new_channel = EmailChannel(
                    name=request.form['name'],
                    email=request.form['email'],
                    user_id=current_user.id
                )
            else:
                return "Invalid channel type", 400

            db.session.add(new_channel)
            db.session.commit()
            return redirect(url_for('notification_channels.index'))
        else:
            return form.errors, 400


@bp.route('<channel_id>/details', methods=["GET"])
@login_required
def details(channel_id):
    notification_channel = NotificationChannel.query.get(channel_id)
    if notification_channel.user.id != current_user.id:
        return "", 404
    return render_template('notification_channels/details.html', notification_channel=notification_channel)
    
@bp.route('<channel_id>/edit', methods=["GET", "POST"])
@login_required
def edit(channel_id):
    notification_channel = NotificationChannel.query.get(channel_id)
    
    if notification_channel.type == "email":
        form = EmailChannelForm()
    else:
        return "", 404 # not other notification channels yet
        
    form.process(obj=notification_channel)
    
    if notification_channel.user.id != current_user.id:
        return "", 404

    if request.method == "GET":
        return render_template(f'notification_channels/edit_{notification_channel.type}.html',
                                form=form, 
                                notification_channel=notification_channel)
    elif request.method == "POST":
        form.process(formdata=request.form)
        if form.validate_on_submit():
            notification_channel.name = request.form["name"]
            if notification_channel.type == "email":
                notification_channel.email = request.form["email"]
            else:
                notification_channel.type = request.form["type"]
                notification_channel.value = request.form["value"]
            db.session.commit()
            return redirect(url_for('notification_channels.details', channel_id = channel_id))
        else:
            return form.errors, 400


@bp.route('delete', methods=["POST"])
@login_required
def delete():
    notification_channel = NotificationChannel.query.get(request.form["notification_channel_id"])
    if notification_channel.user.id != current_user.id:
        return "", 404
    db.session.delete(notification_channel)
    db.session.commit()
    return "success", 200