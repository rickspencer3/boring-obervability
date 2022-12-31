from app.extensions import influxdb_write, mail
from flask import current_app
from flask_mail import Message
from config import Config

def notify(anomaly_detector, check, response):
    current_app.logger.info(f"running anomaly_detector {anomaly_detector.id} of type {anomaly_detector.type} for check {check.id}")
    if anomaly_detector.type == "error":
        _compare(response.status_code, anomaly_detector, check)
    if anomaly_detector.type == "latency":
        _compare(response.elapsed.microseconds * 1000, anomaly_detector, check)

def _send_notifications(anomaly_detector):
    if anomaly_detector.notification_channel is not None:
        channel = anomaly_detector.notification_channel
        current_app.logger.info(f"notifying {channel.name} {channel.type}")
        if channel.type == "email":
            subj = f"Anomaly {anomaly_detector.type} from Anomaly Detector {anomaly_detector.name}"
            message = Message(subj,
                sender=Config.MAIL_DEFAULT_SENDER,
                recipients=[channel.value])
            mail.send(message)
            
def _compare(comparitor, anomaly_detector, check):
    if comparitor >= int(anomaly_detector.value):
        current_app.logger.info(f"anomaly_detector {anomaly_detector.name} ({anomaly_detector.id}) conditions met for check {check.name} ({check.id})")
        lp = f"anomalies,user_id={anomaly_detector.user.id},check={check.id},type={anomaly_detector.type} value={anomaly_detector.value}"
        influxdb_write(lp)
        _send_notifications(anomaly_detector)
    else:
        current_app.logger.info(f"anomaly_detector {anomaly_detector.name} ({anomaly_detector.id}) conditions not met for check {check.name} ({check.id})")
