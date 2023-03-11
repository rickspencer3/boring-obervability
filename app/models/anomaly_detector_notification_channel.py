from app.extensions import db

anomaly_detector_notification_channel = db.Table('anomaly_detector_notification_channel',
                db.Column('anomaly_detector_id', db.Integer, db.ForeignKey('anomaly_detectors.id')),
                db.Column('notification_channel_id', db.Integer, db.ForeignKey('notification_channels.id'))
                )