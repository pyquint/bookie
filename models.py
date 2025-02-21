from flask_login import UserMixin

from app import db, ph


class Book(db.Model):
    __tablename__ = "books"

    book_id = db.Column(db.String, primary_key=True)
    isbn = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    series = db.Column(db.Text, nullable=True)
    author = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    language = db.Column(db.Text, nullable=True)
    genres = db.Column(db.Text, nullable=True)
    characters = db.Column(db.Text, nullable=True)
    book_format = db.Column(db.Text, nullable=True)
    edition = db.Column(db.Text, nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    publisher = db.Column(db.Text, nullable=True)
    publish_date = db.Column(db.Text, nullable=True)
    awards = db.Column(db.Text, nullable=True)
    num_ratings = db.Column(db.Float, nullable=True)
    ratings_by_stars = db.Column(db.Text, nullable=True)
    liked_percent = db.Column(db.Float, nullable=True)
    setting = db.Column(db.Text, nullable=True)
    cover_img = db.Column(db.Text, nullable=True)
    bbe_score = db.Column(db.Float, nullable=True)
    bbe_votes = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"


class User(db.Model, UserMixin):
    __tablename__ = "users"

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    date_created = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        return ph.verify(self.password_hash, password)

    def __repr__(self):
        return f"<User '{self.username}', Date Created {self.date_created}>"
