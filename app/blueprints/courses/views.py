from .import bp as courses
from flask import render_template, request
from app.blueprints.courses.models import Course
from app.blueprints.auth.models import Account
from flask_login import current_user

@courses.route('/')
def index():
    return render_template('courses/index.html', courses=[c for c in Course.query.all()])

@courses.route('/c')
def detail():
    params = request.args
    c = Course.query.filter_by(slug=params.get('name')).first()
    return render_template('courses/detail.html', c=c.to_dict())