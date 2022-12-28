from flask import render_template
from flask_user import login_required
from app.notifications import bp

@bp.route('/')
@login_required
def index():
    print("*******************")
    return render_template('notifications/index.html')