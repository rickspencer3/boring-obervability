from app.extensions import influxdb_write, mail
from flask import current_app
from flask_mail import Message
from config import Config
import json

def notify(anomaly_detector, check, response):
    log_dict = _create_log_dict(anomaly_detector, check)
    if anomaly_detector.type == "error":
        _compare_status(log_dict, anomaly_detector, response)
    elif anomaly_detector.type == "latency":
        _compare_latency(log_dict, anomaly_detector, response)
    
def _compare_status(log_dict, anomaly_detector, response):
    log_dict["comparitor"] = response.status_code
    if int(anomaly_detector.value) >= response.status_code:
        log_dict["detected"] = True
        _send_notifications(anomaly_detector, log_dict)
    else:
        log_dict["detected"] = False
    current_app.logger.info(log_dict)

def _compare_latency(log_dict, anomaly_detector, response):
    log_dict["comparitor"] = response.elapsed.microseconds / 1000
    if response.elapsed.microseconds / 1000 >= int(anomaly_detector.value):
         _send_notifications(anomaly_detector, log_dict)
    else:
        log_dict["detected"] = False
    current_app.logger.info(log_dict)

def _send_notifications(anomaly_detector, log_dict):
    if anomaly_detector.notification_channel is not None:
        channel = anomaly_detector.notification_channel
        current_app.logger.info(f"notifying {channel.name} {channel.type}")
        if channel.type == "email":
            subj = f"Anomaly {anomaly_detector.type} from Anomaly Detector {anomaly_detector.name}"
            message = Message(subj,
                              sender=Config.MAIL_DEFAULT_SENDER,
                              body=json.dumps(log_dict),
                              recipients=[channel.value])
            mail.send(message)

def _create_log_dict(anomaly_detector, check):
    log_dict = {"check_name": check.name,
                "check_id": check.id,
                "anomaly_detector_name": anomaly_detector.name,
                "anomaly_detector_id": anomaly_detector.id,
                "anomaly_detector_type": anomaly_detector.type,
                "anomaly_detector_value": anomaly_detector.value
                }

    return log_dict
