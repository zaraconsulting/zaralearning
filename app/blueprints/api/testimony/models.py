from app import db
from hashlib import md5

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, default=None)
    email = db.Column(db.String)

    def to_dict(self):
        return { 'id': id, 'image': self.image, 'email': self.image }

    def from_dict(self, data):
        for field in ['image', 'email']:
            setattr(self, field, data[field])

    def __init__(self):
        if self.image is None:
            self.image = self.avatar()

    def avatar(self, size):
            return f"https://www.gravatar.com/{md5(self.email.lower().encode('utf-8')).hexdigest()}?d=identicon&s={size}"
