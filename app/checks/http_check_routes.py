from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user

from app.checks import bp
from app.models.checks import HTTPCheck
from app.extensions import db


from app.checks.forms import HTTPForm


@bp.route('/new_http', methods=["GET","POST"])
@login_required
def new_http():
    form = HTTPForm()
    if request.method == "GET":
        return render_template('checks/new_http.html', form=form)

    if request.method == "POST":
        form.process(formdata=request.form)
        if form.validate_on_submit():
            new_check = HTTPCheck()
            form.populate_obj(new_check)
            
            new_check.user_id = current_user.id
            new_check.enabled = True
            new_check.type = "http"
            db.session.add(new_check)
            db.session.commit()
        
            return redirect(url_for('checks.index'))
        else:
            return form.errors, 400

@bp.route('<check_id>/edit_http_check', methods=["POST"])
@login_required
def edit_http(check_id):
    form = HTTPForm()
    check = HTTPCheck.query.get(check_id)
    form.id = check_id
    form.process(obj=check)
    form.process(formdata=request.form)
    if form.validate_on_submit():
        form.populate_obj(check)
        check.enabled = 'enabled' in request.form
        db.session.commit()
        
        return redirect(url_for('checks.details', check_id=check.id))
    else:
        return form.errors, 400
    