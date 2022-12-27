from flask import render_template
from flask_user import login_required, current_user
from app.main import bp

@bp.route('/')
@login_required 
def index():
    checks = current_user.checks
    return render_template('index.html', checks=checks)