from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.notification_channels import bp

@bp.route("/")
@login_required
def index():
    return "boo", 200

