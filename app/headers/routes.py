from app.headers import bp
from flask_user import login_required, current_user
from flask import render_template, request, redirect, url_for


@bp.route('/new', methods=["GET","POST"])
@login_required
def new(id):
    if request.method == "GET":
        return render_template('headers/new.html', id=id)

    if request.method == "POST":
        return redirect(url_for('checks.index'))