from app.extensions import db

class Header(db.Model):
    __tablename__ = 'headers'
    id = db.Column(db.Integer, primary_key = True)
    check_id = db.Column(db.Integer, db.ForeignKey('checks.id'))
    key = db.Column(db.String(100))
    value = db.Column(db.String(100))
    check = db.relationship("Check", back_populates = "headers")