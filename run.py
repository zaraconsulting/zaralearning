from app import db, create_app, cli
from app.blueprints.courses.models import Course, CourseCategory, CourseTag
from app.blueprints.auth.models import Account

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Course': Course, 'CourseCategory':CourseCategory, 'Account': Account, 'CourseTag': CourseTag}
    # return {'db':db, 'Course': Course, 'CourseCategory':CourseCategory, 'CourseTag': CourseTag, 'CourseReview':CourseReview, 'Account': Account}