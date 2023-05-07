## Adding a new type of check
### 1. add the check to `app/models.checks.py`
when you name the type, keep in mind that it will be used to select the proper templates for example:
```Python
return render_template(f'checks/edit_{check.type}.html',
                form=form_classes[check.type](obj=check),
                check=check)
```

### 2. create forms for the check in `app/checks/forms.py`
### 3. use `flask db migrate` and `flask db upgrade` to migrate the database
### 4. create views
 * details
 * new
 * edit
### 5. Add a link the `new_{check.type}.html` to `app/templates/checks/index.html`
### 6. Add a new routes file `app\checks\{check.type}_routes.py`
 * add the route file to `apps\checks\__init__.py`