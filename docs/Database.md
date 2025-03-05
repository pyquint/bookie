Bookie uses [SQLite](https://www.sqlite.org/) populated by this [dataset](https://www.kaggle.com/datasets/pooriamst/best-books-ever-dataset) of around 52,000 book entries of the most ranked books of all time.

# Setup
The database, when fully populated, amounts to some 200 MB. To reduce the project file size for git and GitHub integration, the database is built from the ground up using the the raw CSV file (72 MB).

Simply run `setup.bat` in the `bookie\data` directory.

# SQLAlchemy Models
Currently, the SQLAlchemy models reside in the `models.py` file.

## Books
```python
class Book(db.Model):
    __tablename__ = "books"

    book_id = db.Column(db.Text, primary_key=True)
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
```

## Users
```python
class User(db.Model, UserMixin):
    __tablename__ = "users"

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)

    def get_id(self):
        return self.uid

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            ph.verify(self.password_hash, password)
            return True
        except VerifyMismatchError:
            return False

    def __repr__(self):
        return f"<User {self.username}; Password Hash: {self.password_hash}; Date Created {self.date_created}>"
```

As stated in [Users](Users.md),  `date_created` is a String formatted in ISO 8901.

Checking password hashes is done with`ph`, which is a `PasswordHasher` object from the `argon2` package, declared and imported from `app.py`.

## Comments
```python
class Comment(db.Model):
    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Text, db.ForeignKey("books.book_id"), nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.Text, nullable=False)

    book = db.relationship("Book")
    user = db.relationship("User")

    def __repr__(self):
        return f'<Comment ID: {self.comment_id}; Comment: "{self.comment}"; UID: {self.uid}>'
```

## Flask-Migrate
After setting up the database and structuring the models, it is recommended to use [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) for easier development. The package is already included in the package requirements.

1. `flask db init` - This step can be skipped since the necessary code and folders are already included in the main branch.
2. `flask db migrate`
3. `flask db upgrade`

**Any changes to the models needs to be followed by commands 2 and 3.**

To sync changes, run command 3.


If errors ensue, the forceful approach would be to delete the `migrate` folder and running the commands again.
