from app.extensions import db

class SMSChannel(db.Model):
    __tablename__ = 'sms_channels'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    number = db.Column(db.String(15))
    user = db.relationship("User", back_populates = "sms_channels")

class EmailChannel(db.Model):
    __tablename__ = 'email_channels'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    user = db.relationship("User", back_populates = "email_channels")