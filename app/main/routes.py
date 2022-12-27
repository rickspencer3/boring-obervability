from flask import render_template
from flask_user import login_required
from app.main import bp

@bp.route('/')
@login_required 
def index():
    return render_template('index.html')