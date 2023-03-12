from app.extensions import influxdb_write, mail
from flask import current_app
from flask_user import current_user
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
    if response.status_code >= int(anomaly_detector.value):
        log_dict["detected"] = True
        _handle_anonaly(anomaly_detector, log_dict)
    else:
        log_dict["detected"] = False
    current_app.logger.info(log_dict)

def _compare_latency(log_dict, anomaly_detector, response):
    log_dict["comparitor"] = response.elapsed.microseconds / 1000
    if response.elapsed.microseconds / 1000 >= int(anomaly_detector.value):
         _handle_anonaly(anomaly_detector, log_dict)
    else:
        log_dict["detected"] = False
    current_app.logger.info(log_dict)

def _handle_anonaly(anomaly_detector, log_dict):
    _write_anomaly_to_influxdb(anomaly_detector, log_dict)

    for channel in anomaly_detector.notification_channels:
        if channel.enabled:
            log_dict["channel_name"] = channel.name
            log_dict["channel_type"] = channel.type
            current_app.logger.info(log_dict)
            if channel.type == "email":
                subj = f"Anomaly {anomaly_detector.type} from Anomaly Detector {anomaly_detector.name}"
                message = Message(subj,
                                sender=Config.MAIL_DEFAULT_SENDER,
                                body=json.dumps(log_dict),
                                recipients=[channel.value])
                mail.send(message)
            _write_notification_to_influxdb(channel, log_dict)

def _write_anomaly_to_influxdb(anomaly_detector, log_dict):
    lp = f"anomalies,check={log_dict['check_id']},type={log_dict['anomaly_detector_type']},user_id={anomaly_detector.user_id},id={anomaly_detector.id} value={log_dict['anomaly_detector_value']}"
    influxdb_write(lp)

def _write_notification_to_influxdb(notification_channel, log_dict):
    lp = f"notifications,notification_type={notification_channel.type},check={log_dict['check_id']},anomaly_detector={log_dict['anomaly_detector_id']},user_id={notification_channel.user_id} value={log_dict['anomaly_detector_value']}"
    influxdb_write(lp)

def _create_log_dict(anomaly_detector, check):
    log_dict = {"check_name": check.name,
                "check_id": check.id,
                "anomaly_detector_name": anomaly_detector.name,
                "anomaly_detector_id": anomaly_detector.id,
                "anomaly_detector_type": anomaly_detector.type,
                "anomaly_detector_value": anomaly_detector.value
                }

    return log_dict
