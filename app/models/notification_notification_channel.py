from app.extensions import db

notification_email_channel = db.Table('notification_email_channel',
                db.Column('notification_id', db.Integer, db.ForeignKey('notifications.id')),
                db.Column('email_channel_id', db.Integer, db.ForeignKey('email_channels.id'))
                )

notification_sms_channel = db.Table('notification_sms_channel',
                db.Column('notification_id', db.Integer, db.ForeignKey('notifications.id')),
                db.Column('sms_channel_id', db.Integer, db.ForeignKey('sms_channels.id'))
                )