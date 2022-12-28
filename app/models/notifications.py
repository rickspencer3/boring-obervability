from app.extensions import db
from app.models.notification_notification_channel import notification_email_channel, notification_sms_channel
from app.models.notification_channels import EmailChannel
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key = True)
    check_id = db.Column(db.Integer, db.ForeignKey('checks.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    key = db.Column(db.String(100))
    value = db.Column(db.String(100))
    email_channels = db.relationship('EmailChannel', secondary=notification_email_channel, backref='notifications')
    sms_channels = db.relationship('SMSChannel', secondary=notification_sms_channel, backref='notifications')
    user = db.relationship("User", back_populates = "notifications")