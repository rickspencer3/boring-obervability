from app.extensions import db

class Check(db.Model):
    __tablename__ = 'checks'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    content = db.Column(db.String(600))
    user = db.relationship("User", back_populates = "checks")
