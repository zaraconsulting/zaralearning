from app import db
from datetime import datetime as dt

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    video = db.Column(db.String)
    video_thumbnail = db.Column(db.String)
    icon = db.Column(db.String)
    description = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    reviews = db.relationship('CourseReview', backref='review', cascade="all,delete", lazy='dynamic')
    tags = db.relationship('CourseTag', backref='tag', cascade="all,delete", lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('course_category.id'))

    def create_course(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'video': self.video,
            'video_thumbnail': self.video_thumbnail,
            'description': self.description,
            'date_created': self.date_created,
            'category': CourseCategory.query.get(self.category_id),
            '_tags': CourseTag.query.filter_by(course_id=self.id).all(),
            'tags': ', '.join([t.text for t in CourseTag.query.filter_by(course_id=self.id).all()]),
            'reviews': [r.to_dict() for r in CourseReview.query.filter_by(course_id=self.id).all()],
        }
        return data

    def from_dict(self, data):
        for field in ['name', 'icon', 'video', 'video_thumbnail', 'description', 'category_id']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return f'<Course: {self.name}>'

class CourseReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float)
    text = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    comments = db.relationship('ReviewComment', backref='comment', cascade="all,delete", lazy='dynamic')

    def to_dict(self):
        data = {
            'id': self.id,
            'rating': self.rating,
            'text': self.text,
            'date_created': self.date_created,
            'course': {
                'id': self.course_id,
                'name': Course.query.get(self.course_id).name
            },
            'comments': [c.to_dict() for c in ReviewComment.query.filter_by(review_id=self.id).all()],
        }
        return data

    def from_dict(self, data):
        for field in ['rating', 'text', 'date_created', 'course_id']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return f'<CourseReview: {self.text[20:]}...>'

class CourseTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))

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
    icon = db.Column(db.String)
    courses = db.relationship('Course', backref='course', cascade="all,delete", lazy='dynamic')

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
        }
        return data

    def save(self):
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