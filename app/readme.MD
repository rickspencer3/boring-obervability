

# How to add a resource
 1. create a directory with teh resource name at app/<new-resource>. In that folder create:
    a. __init__.py to the directory, and import the blueprint
    b. routes.py
 2. create new_resource.py in app.models
 3. create a directory in app/templates/<new-resources>, and add index.html to that directory
 4. Open __init__.py at the top level and:
    a. under "associate models here" add any associations
    b. under "Register blueprints here" register the blueprints for the new resources
