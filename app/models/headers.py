from app.extensions import db, generate_id_string
from app.models.header_check import header_check
from cryptography.fernet import Fernet
from flask import current_app

class Header(db.Model):
    __tablename__ = 'headers'
    id = db.Column(db.String(8), primary_key=True, default=generate_id_string)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id')) 
    name = db.Column(db.String(100))
    key = db.Column(db.String(100))
    _value = db.Column("value", db.LargeBinary) 
    user = db.relationship("User", back_populates = "headers")
    checks = db.relationship('Check', secondary=header_check, backref='headers')

    @property
    def value(self):
        f = Fernet(current_app.config['FERNET_KEY'])
        return f.decrypt(self._value).decode('utf-8')

    @value.setter
    def value(self, plaintext_value):
        f = Fernet(current_app.config['FERNET_KEY'])
        self._value = f.encrypt(plaintext_value.encode('utf-8'))