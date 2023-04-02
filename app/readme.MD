

# How to add a resource
 1. create a directory with teh resource name at app/<new-resource>. In that folder create:
    a. __init__.py to the directory, and import the blueprint
    b. routes.py
 2. create new_resource.py in app.models
 3. create a directory in app/templates/<new-resource>, and add index.html to that directory
 4. add a forms.py file to <new-resource>/forms.py and add validators.
 5. create new and edit routes, and new.html and edit.html templates. 

# How to do a Migration
https://flask-migrate.readthedocs.io/en/latest/
