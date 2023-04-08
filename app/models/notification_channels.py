from app.extensions import db, generate_id_string
from app.models.anomaly_detector_notification_channel import anomaly_detector_notification_channel_table
from app.extensions import mail
from flask_mail import Message
from config import Config
import json
class NotificationChannel(db.Model):
    __tablename__ = 'notification_channels'
    id = db.Column(db.String(8), primary_key=True, default=generate_id_string)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id')) 
    name = db.Column(db.String(100))
    type = db.Column(db.String(20), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    user = db.relationship("User", back_populates="notification_channels")
    anomaly_detectors = db.relationship('AnomalyDetector', secondary=anomaly_detector_notification_channel_table, back_populates='notification_channels')

    __mapper_args__ = {
        'polymorphic_identity': 'notification_channel',
        'polymorphic_on': type
    }
    
    def notify(self, obj):
        pass

class EmailChannel(NotificationChannel):
    email = db.Column(db.String(100))

    def notify(self, obj):
        subj = f"Anomaly {self.type} from Anomaly Detector {self.name}"
        message = Message(subj,
                        sender=Config.MAIL_DEFAULT_SENDER,
                        body=json.dumps(obj),
                        recipients=[self.email])
        mail.send(message)

    __mapper_args__ = {
        'polymorphic_identity': 'email',
    }
