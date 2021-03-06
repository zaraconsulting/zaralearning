from app import db, create_app, cli
from app.blueprints.courses.models import Course, CourseCategory, CourseTag, SkillLevel, CourseLearningObjectives
from app.blueprints.auth.models import Account
from app.blueprints.main.models import Testimonial

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Testimonial': Testimonial, 'Course': Course, 'SkillLevel': SkillLevel, 'CourseCategory':CourseCategory, 'Account': Account, 'CourseTag': CourseTag, 'CourseLearningObjectives': CourseLearningObjectives}
    # return {'db':db, 'Course': Course, 'CourseCategory':CourseCategory, 'CourseTag': CourseTag, 'CourseReview':CourseReview, 'Account': Account}