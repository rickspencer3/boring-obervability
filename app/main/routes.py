from flask import render_template
from flask_user import login_required, current_user
from app.main import bp

@bp.route('/', defaults={'time_range': 'h'})
@bp.route('/<time_range>',methods=["GET"])
@login_required 
def index(time_range=None):
    checks = current_user.checks
    return render_template('index.html', checks=checks, time_range=time_range)