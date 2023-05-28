from app.extensions import db, generate_id_string
from app.models.anomaly_detector_check import anomaly_detector_check_table
from app.models.anomaly_detector_notification_channel import anomaly_detector_notification_channel_table
from app.models.anomaly import Anomaly
from app.extensions import influxdb_write

class AnomalyDetector(db.Model):
    """
    Base class for all Anomaly Detectors. Anomaly Detectors are used for detecting abnormal behavior
    in the application. This class defines common properties and methods that all detectors share.
    """

    __tablename__ = 'anomaly_detectors'
    id = db.Column(db.String(8), primary_key=True, default=generate_id_string)  # Unique ID for the detector
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))  # ID of the user who owns this detector
    name = db.Column(db.String(100))  # Name of the detector
    type = db.Column(db.String(10), nullable=False)  # Type of the detector
    checks = db.relationship('Check', secondary=anomaly_detector_check_table)  # List of checks associated with the detector
    notification_channels = db.relationship('NotificationChannel', secondary=anomaly_detector_notification_channel_table)  # List of notification channels associated with the detector
    user = db.relationship("User", back_populates="anomaly_detectors")  # User who owns this detector

    __mapper_args__ = {
        'polymorphic_identity': 'anomaly_detector',
        'polymorphic_on': type
    }

    def detect(self, check_result=None):
        """
        Base method for detecting anomalies. Should be implemented in child classes.
        """
        raise Exception("detect() Not implemented for AnomalyDetector base class")


class LatencyDetector(AnomalyDetector):
    """
    Latency Detector class used to detect anomalies based on latency.
    Inherits from AnomalyDetector.
    """
    latency_lower_bound = db.Column(db.Integer)  # The lower bound for latency to be considered an anomaly

    def detect(self, check_result = None):
        """
        Method to detect latency anomalies. If the check result latency is greater than the lower bound,
        an anomaly is detected, an entry is written in the InfluxDB, and a notification is sent.
        """
        if check_result.latency > self.latency_lower_bound:
            anomaly = Anomaly(check_result, self)
            influxdb_write(anomaly)
            for notification_channel in self.notification_channels:
                notification_channel.notify({})
    
    __mapper_args__ = {
        'polymorphic_identity': 'latency',
    }


class ErrorDetector(AnomalyDetector):
    """
    Error Detector class used to detect anomalies based on errors.
    Inherits from AnomalyDetector.
    """
    def detect(self, check_result=None):
        """
        Method to detect error anomalies. If the check result has an error, 
        an anomaly is detected, an entry is written in the InfluxDB, and a notification is sent.
        """
        if check_result.error:
            anomaly = Anomaly(check_result, self)
            influxdb_write(anomaly)     
            for notification_channel in self.notification_channels:
                notification_channel.notify({})
                
    __mapper_args__ = {
        'polymorphic_identity': 'error',
    }
