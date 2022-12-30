from app.extensions import influxdb_write, mail
from flask import current_app
from flask_mail import Message
from config import Config

def notify(notification, check, response):
    current_app.logger.info(f"running notification {notification.id} of type {notification.type} for check {check.id}")
    if notification.type == "error":
        _compare(response.status_code, notification, check)
    if notification.type == "latency":
        pass

def _send_notifications(notification):
    if notification.notification_channel is not None:
        channel = notification.notification_channel
        current_app.logger.info(f"notifying {channel.name} {channel.type}")
        if channel.type == "email":
            subj = f"notification {notification.type}from notification {notification.name}"
            message = Message(subj,
                sender=Config.MAIL_DEFAULT_SENDER,
                recipients=[channel.value])
            # mail.send(message)
            
def _compare(comparitor, notification, check):
    if comparitor >= int(notification.value):
        current_app.logger.info(f"notification {notification.id} conditions met for check {check.id}")
        lp = f"detected,user_id={notification.user.id},check={check.id},type={notification.type} value={notification.value}"
        influxdb_write(lp)
        _send_notifications(notification)
    else:
        current_app.logger.info(f"notification {notification.id} conditions not metfor check {check.id}")
