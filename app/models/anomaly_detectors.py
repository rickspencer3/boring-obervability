from sqlalchemy.ext.declarative import declared_attr
from app.extensions import db, generate_id_string
from app.models.anomaly_detector_check import anomaly_detector_check_table
from app.models.anomaly_detector_notification_channel import anomaly_detector_notification_channel_table
from app.models.anomaly import Anomaly
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

    def detect(self, check_result=None):
        raise Exception("detect() Not implemented for AnomalyDetector base class")


class LatencyDetector(AnomalyDetector):
    latency_lower_bound = db.Column(db.Integer)

    def detect(self, check_result = None):
        if check_result.latency > self.latency_lower_bound:
            anomaly = Anomaly(check_result, self)
            influxdb_write(anomaly)
            for notificaiton_channel in self.notification_channels:
                notificaiton_channel.notify()
   
            

    __mapper_args__ = {
        'polymorphic_identity': 'latency',
    }

class ErrorDetector(AnomalyDetector):
    def detect(self, check_result=None):
        if check_result.error:
            anomaly = Anomaly(check_result, self)
            influxdb_write(anomaly)     
            for notificaiton_channel in self.notification_channels:
                notificaiton_channel.notify()
                
    __mapper_args__ = {
        'polymorphic_identity': 'error',
    }

