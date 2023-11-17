This project is licensed under the Apache License version 2. See: https://www.apache.org/licenses/LICENSE-2.0

## Adding a new type of check
### 1. add the check to `app/models.checks.py`
when you name the type, keep in mind that it will be used to select the proper templates for example:
```Python
return render_template(f'checks/edit_{check.type}.html',
                form=form_classes[check.type](obj=check),
                check=check)
```
### 2. use `flask db migrate` and `flask db upgrade` to migrate the database
### 3. update CheckClass in `app\models\__init__.py`
### 4. create forms for the check in `app/checks/forms.py`
### 5. update FormClass in `app/checks/forms.py`
### 6. create new view
 * details_{type}.html
 * edit_{type}.html
 * new_{type}.html
### 7. add link to the new route with the type to `app/templates/checks/index.html`
