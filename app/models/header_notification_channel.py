from app.extensions import db

header_notification_channel = db.Table('header_notification_channel',
                db.Column('header_id', db.Integer, db.ForeignKey('headers.id')),
                db.Column('notification_channel_id', db.Integer, db.ForeignKey('notification_channels.id'))
                )