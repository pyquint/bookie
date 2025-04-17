import sqlalchemy as sa
import sqlalchemy.orm as so

from app import create_app, db
from app.models import (
    Author,
    Award,
    Book,
    BookStatus,
    Character,
    Comment,
    Genre,
    Publisher,
    ReadingStatus,
    User,
    UserFavorite,
)

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
        "BookStatus": BookStatus,
        "UserFavorite": UserFavorite,
        "Author": Author,
        "Award": Award,
        "Character": Character,
        "Genre": Genre,
        "Publisher": Publisher,
    }
