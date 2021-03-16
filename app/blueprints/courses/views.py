from .import bp as courses
from flask import render_template, request
from app.blueprints.courses.models import Course

@courses.route('/')
def index():
    return render_template('courses/index.html', courses=[c for c in Course.query.all()])

@courses.route('/course')
def detail():
    params = request.args
    c = Course.query.get(params.get('id'))
    # print(c.to_dict())
    return render_template('courses/detail.html', c=c)