from .import bp as courses
from flask import render_template, request, redirect, url_for, current_app as app
from app.blueprints.courses.models import Course, CourseCategory, CourseTag
from app.blueprints.auth.models import Account
from flask_login import current_user
from sqlalchemy import or_

@courses.route('/', methods=['POST', 'GET'])
def index():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.paginate(page, app.config.get('POSTS_PER_PAGE'), False)
    next_url = url_for('courses.index', page=courses.next_num) if courses.has_next else None
    prev_url = url_for('courses.index', page=courses.prev_num) if courses.has_prev else None
    return render_template('courses/index.html', next_url=next_url, prev_url=prev_url, courses=courses.items)

@courses.route('/s')
def search():
    page = request.args.get('page', 1, type=int)
    if request.args.get('search') is not None:
        search = request.args.get('search')
        courses = Course.query.filter(or_(Course.description.ilike(f'%{search}%'), Course.name.ilike(f'%{search}%'))).paginate(page, app.config.get('POSTS_PER_PAGE'), False)
    else:
        courses = Course.query.paginate(page, app.config.get('POSTS_PER_PAGE'), False)
    next_url = url_for('courses.index', page=courses.next_num) if courses.has_next else None
    prev_url = url_for('courses.index', page=courses.prev_num) if courses.has_prev else None
    return render_template('courses/index.html', next_url=next_url, prev_url=prev_url, courses=courses.items)

@courses.route('/c')
def detail():
    params = request.args
    c = Course.query.filter_by(slug=params.get('name')).first()
    related = [i.to_dict() for i in Course.query.filter_by(category_id=c.id).all()]
    return render_template('courses/detail.html', c=c.to_dict(), related=related)

@courses.route('/category')
def category():
    page = request.args.get('page', 1, type=int)
    cat = CourseCategory.query.filter_by(slug=request.args.get('name')).first()
    courses = Course.query.filter_by(category_id=cat.id).paginate(page, app.config.get('POSTS_PER_PAGE'), False).items
    return render_template('courses/index.html', courses=courses)

@courses.route('/tags')
def tags():
    tag = request.args.get('name')
    courses = []
    for c in Course.query.all():
        if tag in [i.text for i in c.tags.all()]:
            courses.append(c)
    return render_template('courses/index.html', courses=courses)