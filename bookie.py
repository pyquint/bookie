import sqlalchemy as sa
import sqlalchemy.orm as so

from app import create_app, db
from app.models import Book, BookStatus, Comment, ReadingStatus, User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "sa": sa,
        "so": so,
        "db": db,
        "Book": Book,
        "User": User,
        "Comment": Comment,
        "ReadingStatus": ReadingStatus,
        "BookStatus": BookStatus
    }
