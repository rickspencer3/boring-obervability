from sqlalchemy.ext.declarative import declared_attr
from app.extensions import db
from app.models.anomaly_detector_check import anomaly_detector_check_table
from app.models.anomaly_detector_notification_channel import anomaly_detector_notification_channel_table


class AnomalyDetector(db.Model):
    __tablename__ = 'anomaly_detectors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    type = db.Column(db.String(10), nullable=False)
    checks = db.relationship('Check', secondary=anomaly_detector_check_table)
    notification_channels = db.relationship('NotificationChannel', secondary=anomaly_detector_notification_channel_table, uselist=False)
    user = db.relationship("User", back_populates="anomaly_detectors")

    __mapper_args__ = {
        'polymorphic_identity': 'anomaly_detector',
        'polymorphic_on': type
    }

    def detect(self, check=None, response=None):
        pass

    def _create_log_dict(self, check):
        log_dict = {"check_name": check.name,
                    "check_id": check.id,
                    "anomaly_detector_name": self.name,
                    "anomaly_detector_id": self.id,
                    "anomaly_detector_type": self.type
                    }

        return log_dict


class LatencyDetector(AnomalyDetector):
    latency_lower_bound = db.Column(db.Integer)

    def detect(self, check=None, response=None):
        log_dict = self._create_log_dict(check)
        db.app.logger.info(log_dict)

    def _create_log_dict(self, check):
        d = super()._create_log_dict(check)
        d["status_lower_bound"] = self.latency_lower_bound
        return d
    __mapper_args__ = {
        'polymorphic_identity': 'latency',
    }

class ErrorDetector(AnomalyDetector):
    status_lower_bound = db.Column(db.Integer)

    def detect(self, check=None, response=None):
        log_dict = self._create_log_dict(check)
        db.app.logger.info(log_dict)        

    def _create_log_dict(self, check):
        d = super()._create_log_dict(check)
        d["status_lower_bound"] = self.status_lower_bound
        return d

    __mapper_args__ = {
        'polymorphic_identity': 'error',
    }

