from app import db
from datetime import datetime as dt
from hashlib import md5
from statistics import mean
from app.blueprints.auth.models import Account


class CourseWatcher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_level_id = db.Column(db.Integer, db.ForeignKey('skill_level.id'))
    name = db.Column(db.String)
    video = db.Column(db.String)
    video_thumbnail = db.Column(db.String)
    icon = db.Column(db.String)
    # TODO: Make a Video class to keep track of videos
    video_length = db.Column(db.Float)
    icon = db.Column(db.String)
    description = db.Column(db.Text)
    slug = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    reviews = db.relationship('CourseReview', backref='review', cascade="all,delete", lazy='dynamic')
    tags = db.relationship('CourseTag', backref='tag', cascade="all,delete", lazy='dynamic')
    learning_objectives = db.relationship('CourseLearningObjectives', backref='learning_objects', lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('course_category.id'))

    def slugify(self):
        self.slug = self.name.lower().replace(' ', '-')

    def save(self):
        self.slugify()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'slug': self.slug,
            'video': self.video,
            'skill_level': SkillLevel.query.get(self.skill_level_id),
            'video_thumbnail': self.video_thumbnail,
            'video_length': self.video_length,
            'learning_objectives': self.learning_objectives,
            'description': self.description,
            'date_created': self.date_created,
            'category': CourseCategory.query.get(self.category_id),
            'tags_': CourseTag.query.filter_by(course_id=self.id).all(),
            '_tags': CourseTag.query.filter_by(course_id=self.id).all(),
            'tags': ', '.join([t.text for t in CourseTag.query.filter_by(course_id=self.id).all()]),
            'reviews': {
                'list': [r.to_dict() for r in CourseReview.query.filter_by(course_id=self.id).all()],
                'avg': {
                    'value': float(mean([i.rating for i in self.reviews.all() if i.rating])) if self.reviews.all() else float(0),
                    'stars': range(int(mean([i.rating for i in self.reviews.all() if i.rating]))) if self.reviews.all() else []
                }
            },
            'viewers': {
                'list': [i for i in CourseWatcher.query.filter_by(course_id=self.id).all()]
            }
        }
        return data

    def from_dict(self, data):
        for field in ['name', 'icon', 'video', 'video_thumbnail', 'skill_level_id', 'video_length', 'description', 'category_id']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return f'<Course: {self.name}>'


class CourseLearningObjectives(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def __repr__(self):
        return f'<CourseLearningObjectives: {self.description}>'

class SkillLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    courses = db.relationship('Course', backref='course', cascade="all,delete", lazy='dynamic')


class CourseTestimonials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class CourseReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    name = db.Column(db.String)
    email = db.Column(db.String)
    text = db.Column(db.Text)
    avatar = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    comments = db.relationship('ReviewComment', backref='comment', cascade="all,delete", lazy='dynamic')

    def avatar(self, size=80):
        return f"https://www.gravatar.com/{md5(self.email.lower().encode('utf-8')).hexdigest()}?d=identicon&s={size}"

    def save(self):
        self.avatar = self.avatar()
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        data = {
            'id': self.id,
            'rating': range(int(self.rating or 5)),
            'avatar': self.avatar,
            'name': self.name,
            'email': self.email,
            'text': self.text,
            'date_created': self.date_created,
            'course': {
                'id': self.course_id,
                'name': Course.query.get(self.course_id).name
            },
            'comments': [c.to_dict() for c in ReviewComment.query.filter_by(review_id=self.id).order_by(ReviewComment.date_created.desc()).all()],
        }
        return data

    def from_dict(self, data):
        for field in ['name', 'rating', 'email', 'text', 'course_id']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return f'<CourseReview: {self.text[20:]}...>'

class CourseTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    slug = db.Column(db.String)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    
    def slugify(self):
        self.slug = self.text.lower().replace(' ', '-')


    def save(self):
        self.slugify()
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'slug': self.slug,
            'course': Course.query.get(self.course_id).to_dict()
        }

    def __repr__(self):
        return f'<CourseTag: {self.text}...>'

class ReviewComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    review_id = db.Column(db.Integer, db.ForeignKey('course_review.id', ondelete='CASCADE'))
    date_created = db.Column(db.DateTime, default=dt.utcnow)

    def to_dict(self):
        data = {
            'id': self.id,
            'text': self.text,
            'course_review_id': self.review_id,
            'date_created': self.date_created
        }
        return data


    def from_dict(self, data):
        for field in ['text', 'course_review_id', 'date_created']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return f'<ReviewComment: {self.text[20:]}...>'


class CourseCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    slug = db.Column(db.String)
    image = db.Column(db.String)
    icon = db.Column(db.String)
    courses = db.relationship('Course', backref='courses', cascade="all,delete", lazy='dynamic')

    def slugify(self):
        self.slug = self.name.lower().replace(' ', '-')

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'image': self.image,
            'icon': self.icon,
            'courses': [i.to_dict() for i in self.courses.all()],
        }
        return data

    def from_dict(self, data):
        for field in ['name', 'image', 'icon']:
            if field in data:
                setattr(self, field, data[field])

    def save(self):
        self.slugify()
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.remove(self)
        db.session.commit()

    def from_dict(self, data):
        for field in ['name', 'icon']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return f'<CourseCategory: {self.name}...>'