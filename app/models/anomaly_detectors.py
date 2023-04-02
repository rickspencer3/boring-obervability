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

    def detect(self):
        pass


class LatencyDetector(AnomalyDetector):
    latency_lower_bound = db.Column(db.Integer)

    def detect(self):
        print(" ***** detecting latency")

    __mapper_args__ = {
        'polymorphic_identity': 'latency',
    }

class ErrorDetector(AnomalyDetector):
    status_lower_bound = db.Column(db.Integer)

    def detect(self):
        print(" ***** detecting error")

    __mapper_args__ = {
        'polymorphic_identity': 'error',
    }
