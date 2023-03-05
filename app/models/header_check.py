from app.extensions import db

header_check = db.Table('header_check',
                db.Column('header_id', db.Integer, db.ForeignKey('headers.id')),
                db.Column('check_id', db.Integer, db.ForeignKey('checks.id'))
                )