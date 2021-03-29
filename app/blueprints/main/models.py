from app import db
from hashlib import md5

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, default=None)
    name = db.Column(db.String)
    message = db.Column(db.String)
    rating = db.Column(db.Integer)
    email = db.Column(db.String)
    occupation = db.Column(db.String)

    def to_dict(self):
        return { 'id': id, 'image': self.image, 'name': self.name, 'message': self.message, 'rating': range(int(self.rating)), 'email': self.image, 'occupation': self.occupation }

    def from_dict(self, data):
        for field in ['name', 'email', 'message', 'rating', 'email', 'occupation']:
            setattr(self, field, data[field])

    def __init__(self, name=name, occupation=occupation, message=message, rating=rating, image=image, email=email):
        self.email = email
        self.name = name
        self.message = message
        self.rating = rating
        self.occupation = occupation
        if self.image is None:
            self.image = self.avatar()

    def avatar(self, size=80):
            return f"https://www.gravatar.com/{md5(self.email.lower().encode('utf-8')).hexdigest()}?d=identicon&s={size}"
