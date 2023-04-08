from sqlalchemy.ext.declarative import declared_attr
from app.extensions import db, generate_id_string
from app.models.anomaly_detector_check import anomaly_detector_check_table
from app.models.anomaly_detector_notification_channel import anomaly_detector_notification_channel_table
from app.extensions import influxdb_write
from flask import current_app

class AnomalyDetector(db.Model):
    __tablename__ = 'anomaly_detectors'
    id = db.Column(db.String(8), primary_key=True, default=generate_id_string)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id')) 
    name = db.Column(db.String(100))
    type = db.Column(db.String(10), nullable=False)
    checks = db.relationship('Check', secondary=anomaly_detector_check_table)
    notification_channels = db.relationship('NotificationChannel', secondary=anomaly_detector_notification_channel_table)
    user = db.relationship("User", back_populates="anomaly_detectors")

    __mapper_args__ = {
        'polymorphic_identity': 'anomaly_detector',
        'polymorphic_on': type
    }

    def detect(self, check=None, response=None):
        pass

    def _create_log_dict(self, check, response):
        log_dict = {"check_name": check.name,
                    "check_id": check.id,
                    "anomaly_detector_name": self.name,
                    "anomaly_detector_id": self.id,
                    "anomaly_detector_type": self.type,
                    "response_status": response.status_code,
                    "response_latency": response.elapsed.microseconds / 1000
                    }

        return log_dict

class LatencyDetector(AnomalyDetector):
    latency_lower_bound = db.Column(db.Integer)

    def detect(self, check=None, response=None):
        log_dict = self._create_log_dict(check, response)
        latency = response.elapsed.microseconds / 1000
        detected = latency > self.latency_lower_bound
        log_dict['detected'] = detected

        if detected:
            lp = f"anomalies,check={check.id},type={self.type},user_id={self.user_id},id={self.id} latency_bound={self.latency_lower_bound},observed={latency}"
            influxdb_write(lp)
            for channel in self.notification_channels:
                channel.notify(log_dict)
                
        current_app.logger.info(log_dict)

    def _create_log_dict(self, check, response):
        d = super()._create_log_dict(check, response)
        d["status_lower_bound"] = self.latency_lower_bound
        return d

    __mapper_args__ = {
        'polymorphic_identity': 'latency',
    }

class ErrorDetector(AnomalyDetector):
    status_lower_bound = db.Column(db.Integer)

    def detect(self, check=None, response=None):
        log_dict = self._create_log_dict(check, response)
        detected = response.status_code > self.status_lower_bound
        log_dict['detected'] = detected

        if detected:
            lp = f"anomalies,check={check.id},type={self.type},user_id={self.user_id},id={self.id} status_bound={self.status_lower_bound},observed={response.status_code}"
            influxdb_write(lp)
            for channel in self.notification_channels:
                channel.notify(log_dict)

        current_app.logger.info(log_dict)        

    def _create_log_dict(self, check, response):
        d = super()._create_log_dict(check, response)
        d["status_lower_bound"] = self.status_lower_bound
        return d

    __mapper_args__ = {
        'polymorphic_identity': 'error',
    }

