from app.extensions import db
from app.models.checks import Check
class HTTPCheck(Check):
    content = db.Column(db.String(600))
    method = db.Column(db.String(10))
    url = db.Column(db.String(100))

    __mapper_args__ = {
    'polymorphic_identity': 'http',
    }

    def run(self):
        print(f"run HTTPCheck {self.id}, {self.name}")
    
    @property
    def form_class(self):
        import app.checks.forms as forms
        return forms.HTTPForm