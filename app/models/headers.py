from app.extensions import db
from app.models.header_check import header_check
class Header(db.Model):
    __tablename__ = 'headers'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    key = db.Column(db.String(100))
    value = db.Column(db.String(100))
    user = db.relationship("User", back_populates = "headers")
    checks = db.relationship('Check', secondary=header_check, backref='headers')