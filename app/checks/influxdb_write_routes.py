from flask import render_template, request, redirect, url_for
from flask_user import login_required, current_user

from app.checks import bp
from app.models.checks import InfluxDBWriteCheck
from app.extensions import db


from app.checks.forms import InfluxDBWriteForm

@bp.route('/new_influxdb_write', methods=["GET", "POST"])
@login_required
def new_influxdb_write():
    form = InfluxDBWriteForm()
    if request.method == "GET":
        return render_template('checks/new_influxdb_write.html', form=form)

    if request.method == "POST":
        form.process(formdata=request.form)
        if form.validate_on_submit():
            new_check = InfluxDBWriteCheck()
            form.populate_obj(new_check)
            
            new_check.user_id = current_user.id
            new_check.enabled = True
            new_check.type = "influxdb_write"
            db.session.add(new_check)
            db.session.commit()
        
            return redirect(url_for('checks.index'))
        else:
            return form.errors, 400

