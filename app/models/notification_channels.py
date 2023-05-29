from app.extensions import db, generate_id_string
from app.models.anomaly_detector_notification_channel import anomaly_detector_notification_channel_table
from app.extensions import mail
from flask_mail import Message
from config import Config
import requests

class NotificationChannel(db.Model):
    """
    Base class for all Notification Channels. Notification Channels are used for alerting users
    about detected anomalies. This class defines common properties and methods that all channels share.
    """
    __tablename__ = 'notification_channels'
    id = db.Column(db.String(8), primary_key=True, default=generate_id_string)  # Unique ID for the notification channel
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))  # ID of the user who owns this channel
    name = db.Column(db.String(100))  # Name of the channel
    type = db.Column(db.String(20), nullable=False)  # Type of the channel
    enabled = db.Column(db.Boolean, default=True)  # Boolean indicating if the channel is enabled or not
    user = db.relationship("User", back_populates="notification_channels")  # User who owns this channel
    anomaly_detectors = db.relationship('AnomalyDetector', secondary=anomaly_detector_notification_channel_table, back_populates='notification_channels')  # List of anomaly detectors associated with this channel

    __mapper_args__ = {
        'polymorphic_identity': 'notification_channel',
        'polymorphic_on': type
    }

    def notify(self, msg):
        """
        Base method for sending notifications. Should be implemented in child classes.
        """
        pass

class EmailChannel(NotificationChannel):
    """
    Email Channel class used to send email notifications.
    Inherits from NotificationChannel.
    """
    email = db.Column(db.String(100))  # Email address to which the notifications should be sent

    def notify(self, msg):
        """
        Method to send email notifications. A message with a subject and body is created and sent
        to the email address associated with this channel.
        """
        subj = f"Anomaly {self.type} from Anomaly Detector {self.name}"
        message = Message(subj,
                        sender=Config.MAIL_DEFAULT_SENDER,
                        body=msg,
                        recipients=[self.email])
        mail.send(message)

    __mapper_args__ = {
        'polymorphic_identity': 'email',
    }

class WebhookChannel(NotificationChannel):
    """
    Webhook Channel class used to send notifications to a specified URL.
    Inherits from NotificationChannel.
    """
    url = db.Column(db.String(2048))  # URL to which the notifications should be sent

    def notify(self, msg):
        """
        Method to send webhook notifications. A POST request with headers and body is created and sent
        to the URL associated with this channel.
        """
        # create the headers dict from the related Header objects
        headers_dict = {header.name: header.value for header in self.headers}
        
        # POST request to the webhook URL
        response = requests.post(self.url, headers=headers_dict, json=msg)
        
        # You might want to handle possible HTTP errors here, or have a way of logging them
        if response.status_code != 200:
            print(f"Webhook POST request failed with status {response.status_code}")
        
    __mapper_args__ = {
        'polymorphic_identity': 'webhook',
    }

