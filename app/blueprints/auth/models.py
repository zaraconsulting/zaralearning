from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime as dt
from flask import current_app
import jwt, time
from werkzeug.security import generate_password_hash, check_password_hash

class Account(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    is_customer = db.Column(db.Boolean, default=False)
    customer_id = db.Column(db.String, unique=True)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    # courses_watch
    # role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    # is_admin = db.Column(db.Boolean, default=0)
    # role_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=Role.query.filter_by(name='User').first())

    def get_reset_password_token(self, expires_in=600):
        # print(current_app.config.get('SECRET_KEY'))
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in }, current_app.config.get('SECRET_KEY'), algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])['reset_password']
        except:
            return
        return Account.query.get(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)
        return self.password

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        data = {
            'email': self.email,
            'name': self.name,
            'customer': {'id': self.customer_id, 'is_customer': self.is_customer},
            'password': self.password,
            'date_created': self.date_created
        }
        return data

    def from_dict(self, data):
        for field in ['name', 'email', 'password']:
            if field in data:
                setattr(self, field, data[field])

    def __str__(self):
        return self.email

    def __repr__(self):
        return self.email

@login_manager.user_loader
def load_account(id):
    return Account.query.get(int(id))
    # return Customer.query.get(int(id)) or Account.query.get(int(id))