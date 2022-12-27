from flask import Flask
from flask_user.user_manager import UserManager
from config import Config
from app.extensions import db

from app.models.users import User
from app.models.checks import Check
from app.models.headers import Header
from app.check_job import run_checks

from apscheduler.schedulers.background import BackgroundScheduler


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Initialize Flask extensions here
    db.init_app(app)
    db.app = app

    User.checks = db.relationship(
        "Check", order_by=Check.id, back_populates="user")
    Check.headers = db.relationship(
        "Header", order_by=Header.id, back_populates="check")
    with app.app_context():
        db.create_all()
        user_manager = UserManager(app, db, User)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.checks import bp as checks_bp
    app.register_blueprint(checks_bp, url_prefix='/checks')

    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/users')

    from app.headers import bp as headers_bp
    app.register_blueprint(headers_bp, url_prefix='/headers')

    # schedule the checks
    scheduler = BackgroundScheduler()
    with app.app_context():
        checks = Check.query.all()
        for check in checks:
            scheduler.add_job(run_checks, 'interval',  
                            str(check.id),  seconds=5)
    scheduler.start()

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app
