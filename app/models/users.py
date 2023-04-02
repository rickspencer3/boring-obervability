from app.extensions import db
from flask_user import UserMixin
from app.models.checks import Check
from app.models.notification_channels import NotificationChannel
from app.models.headers import Header

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    # email_confirmed_at = db.Column(db.DateTime())
    # email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    
    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    anomaly_detectors = db.relationship("AnomalyDetector", back_populates="user", cascade="all, delete-orphan")
    checks = db.relationship("Check", order_by=Check.id, back_populates="user")
    headers = db.relationship("Header", order_by=Header.id, back_populates="user")
    notification_channels = db.relationship("NotificationChannel", order_by=NotificationChannel.id, back_populates="user")
