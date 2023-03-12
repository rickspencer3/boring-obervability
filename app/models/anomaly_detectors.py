from app.extensions import db
from app.models.anomaly_detector_check import anomaly_detector_check
from app.models.anomaly_detector_notification_channel import anomaly_detector_notification_channel
class AnomalyDetector(db.Model):
    __tablename__ = 'anomaly_detectors'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    key = db.Column(db.String(100))
    value = db.Column(db.String(100))
    type = db.Column(db.String(10))
    checks = db.relationship('Check', secondary=anomaly_detector_check, backref='anomaly_detectors')
    user = db.relationship("User", back_populates = "anomaly_detectors")
    