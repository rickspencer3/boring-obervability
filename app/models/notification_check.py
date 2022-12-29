from app.extensions import db

notification_check = db.Table('notification_check',
                db.Column('notification_id', db.Integer, db.ForeignKey('notifications.id')),
                db.Column('check_id', db.Integer, db.ForeignKey('checks.id'))
                )