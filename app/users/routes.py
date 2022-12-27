from flask import render_template
from app.users import bp

@bp.route('/')
def index():
    return render_template('users/index.html')