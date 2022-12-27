from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user
from app.checks import bp
from app.models.checks import Check
from app.extensions import db

@bp.route('/')
@login_required
def index():
    all_checks = Check.query.all()
    return render_template('checks/index.html', checks = all_checks)

@bp.route('/<id>')
@login_required
def details(id):
    check = Check.query.get(id)
    return render_template('checks/details.html', check=check)

@bp.route('/<id>/headers')
@login_required
def new_header(id):
    return render_template('headers/new.html', id=id)

@bp.route('/new', methods=["GET","POST"])
@login_required
def new():
    if request.method == "GET":
        return render_template('checks/new.html')

    if request.method == "POST":
        new_check = Check(name = request.form['name'], 
        url = request.form['url'],
        user_id = current_user.id)
        db.session.add(new_check)
        db.session.commit()
       
        return redirect(url_for('checks.index'))