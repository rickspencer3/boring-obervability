import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'BeTjncDRQSvNbH0LLXHTMJg9gds16n9z'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_SERVER = ''
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = ''

    # Flask-User settings
    USER_APP_NAME = "Boring Observability"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form

    # InfluxDB settings
    INFLUXDB_BUCKET = ""
    INFLUXDB_WRITE_TOKEN = "=="
    INFLUXDB_READ_TOKEN = "=="
    INFLUXDB_HOST = ""
    INFLUXDB_FLIGHT_HOST = ""
    INFLUXDB_ORG_ID = ""
    FERNET_KEY = ""
    