from .import bp as main
from flask import render_template, current_app as app
from app.blueprints.courses.models import CourseCategory, Course

@main.route('/')
def home():
    context = {
        'course_categories': CourseCategory.query.order_by(CourseCategory.name).all(),
        'courses': Course.query.all(),
        'subscription_basic': app.config.get('SUBSCRIPTION_BASIC')
    }
    return render_template('home.html', **context)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')