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

@bp.route('/<header_id>', methods=["GET"])
@login_required
def details(header_id):
    header = Header.query.get(header_id)
    if header.user_id != current_user.id:
        return "", 404
    return render_template('headers/details.html', header=header)

@bp.route('/<header_id>/edit', methods=["GET","POST"])
@login_required
def edit(header_id):
    header = Header.query.get(header_id)
    if header.user_id != current_user.id:
        return "", 404
    if request.method == "GET":
        return render_template('headers/edit.html', header=header)
    elif request.method == "POST":
        header.name = request.form["name"]
        header.key = request.form["key"]
        header.value = request.form["value"]
        db.session.commit()
        return redirect(url_for('headers.details', header_id=header.id))

@bp.route('/<header_id>/delete', methods=["POST"])
@login_required
def delete(header_id):
    return redirect(url_for('headers.index'))

@bp.route('/', methods=["GET","POST"])
@login_required
def index():
    headers = current_user.headers
    return render_template('headers/index.html', headers = headers)