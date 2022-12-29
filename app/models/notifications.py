from app.extensions import db
from app.models.notification_channels import NotificationChannel
from app.models.notification_check import notification_check

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notification_channel_id = db.Column(db.Integer, db.ForeignKey('notification_channels.id'))
    name = db.Column(db.String(100))
    key = db.Column(db.String(100))
    value = db.Column(db.String(100))
    type = db.Column(db.String(10))
    checks = db.relationship('Check', secondary=notification_check, backref='notifications')
    user = db.relationship("User", back_populates = "notifications")
    notification_channel = db.relationship("NotificationChannel", back_populates = "notifications")
    