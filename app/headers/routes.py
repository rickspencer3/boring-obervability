from app.headers import bp
from app.extensions import db
from app.models.headers import Header
from flask_user import login_required, current_user
from flask import render_template, request, redirect, url_for


@bp.route('/new', methods=["GET","POST"])
@login_required
def new(id=None):
    if request.method == "GET":
        return render_template('headers/new.html', id=id)

    if request.method == "POST":
        header = Header(name = request.form['name'],
                key = request.form['key'], 
                value = request.form['value'])
        header.user = current_user
        db.session.add(header)
        db.session.commit()
        return redirect(url_for('headers.index'))

@bp.route('/', methods=["GET","POST"])
@login_required
def index():
    headers = current_user.headers
    return render_template('headers/index.html', headers = headers)