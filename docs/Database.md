Bookie uses [SQLite](https://www.sqlite.org/) populated by this [dataset](https://www.kaggle.com/datasets/pooriamst/best-books-ever-dataset) of around 52,000 book entries of the most ranked books of all time.

# Setup
The database, when fully populated, amounts to some 200 MB. To reduce the project file size for git and GitHub integration, the database is built from the ground up using the the raw CSV file (72 MB).

Simply run `setup.bat` in the `bookie\data` directory.

# SQLAlchemy Models
Currently, the SQLAlchemy models reside in `app\models.py`.

## [Books](Books.md)

## [Users](Users.md)

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

To sync changes after pulling a commit with no db changes, run command 3.
Otherwise, run `setup.py` to automatically re-initialize the database.


If errors ensue, the forceful approach would be to delete the `migrate` folder and running the commands again.
