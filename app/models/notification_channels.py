from app.extensions import db
from app.models.anomaly_detector_notification_channel import anomaly_detector_notification_channel
class NotificationChannel(db.Model):
    __tablename__ = 'notification_channels'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    value = db.Column(db.String(100))
    type = db.Column(db.String(20))
    enabled = db.Column(db.Boolean, default=True)
    user = db.relationship("User", back_populates = "notification_channels")
    anomaly_detectors = db.relationship('AnomalyDetector', secondary=anomaly_detector_notification_channel, backref='notification_channels', uselist=False)
    