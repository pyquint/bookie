from datetime import datetime, timezone
from typing import Optional, Type

import sqlalchemy as sa
from argon2.exceptions import VerifyMismatchError
from flask import url_for
from flask_login import UserMixin
from flask_sqlalchemy.model import Model
from sqlalchemy.orm import (
    DynamicMapped,
    Mapped,
    WriteOnlyMapped,
    mapped_column,
    relationship,
)

from app import db, login_manager, ph


@login_manager.user_loader
def load_user(id):
    return db.session.get(User, id)


# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxiii-application-programming-interfaces-apis


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = db.paginate(query, page=page, per_page=per_page, error_out=False)
        data = {
            "items": [item.to_dict() for item in resources.items],
            "_meta": {
                "page": page,
                "per_page": per_page,
                "total_pages": resources.pages,
                "total_items": resources.total,
            },
            "_links": {
                "self": url_for(endpoint, page=page, per_page=per_page, **kwargs),
                "next": (
                    url_for(endpoint, page=page + 1, per_page=per_page, **kwargs)
                    if resources.has_next
                    else None
                ),
                "prev": (
                    url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
                    if resources.has_prev
                    else None
                ),
            },
        }
        return data


class Book(db.Model, PaginatedAPIMixin):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    isbn: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column()
    book_format: Mapped[str] = mapped_column()
    language: Mapped[str] = mapped_column()
    series: Mapped[str] = mapped_column()
    edition: Mapped[str] = mapped_column()
    cover_img: Mapped[str] = mapped_column()

    rating: Mapped[float] = mapped_column(index=True)
    num_ratings: Mapped[int] = mapped_column(index=True)
    bbe_score: Mapped[int] = mapped_column()
    bbe_votes: Mapped[int] = mapped_column()

    five_star_ratings: Mapped[int] = mapped_column()
    four_star_ratings: Mapped[int] = mapped_column()
    three_star_ratings: Mapped[int] = mapped_column()
    two_star_ratings: Mapped[int] = mapped_column()
    one_star_ratings: Mapped[int] = mapped_column()

    pages: Mapped[Optional[int]] = mapped_column()
    price: Mapped[Optional[float]] = mapped_column()
    liked_percent: Mapped[Optional[float]] = mapped_column()

    publish_date: Mapped[Optional[datetime]] = mapped_column()
    publish_date_format: Mapped[Optional[str]] = mapped_column()
    first_publish_date: Mapped[Optional[datetime]] = mapped_column()
    first_publish_date_format: Mapped[Optional[str]] = mapped_column()

    authors: Mapped[list["Author"]] = relationship(
        back_populates="books", secondary="book_authors"
    )
    genres: Mapped[list["Genre"]] = relationship(
        back_populates="books", secondary="book_genres"
    )
    characters: Mapped[list["Character"]] = relationship(
        back_populates="books", secondary="book_characters"
    )
    awards: Mapped[list["Award"]] = relationship(
        back_populates="books", secondary="book_awards"
    )
    settings: Mapped[list["Setting"]] = relationship(
        back_populates="books", secondary="book_settings"
    )
    publisher: Mapped["Publisher"] = relationship(
        back_populates="books", secondary="book_publisher"
    )

    comments: DynamicMapped[list["Comment"]] = relationship(back_populates="book")
    favorited_by: Mapped[list["User"]] = relationship(secondary="user_favorites")
    book_statuses: WriteOnlyMapped[list["BookStatus"]] = relationship(
        back_populates="book", lazy="dynamic"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "series": self.series,
            "rating": self.rating,
            "description": self.description,
            "language": self.language,
            "isbn": self.isbn,
            "book_format": self.book_format,
            "edition": self.edition,
            "pages": self.pages,
            "publish_date": self.publish_date,
            "publish_date_format": self.publish_date_format,
            "first_publish_date": self.first_publish_date,
            "first_publish_date_format": self.first_publish_date_format,
            "num_ratings": self.num_ratings,
            "star_ratings": [
                self.one_star_ratings,
                self.two_star_ratings,
                self.three_star_ratings,
                self.four_star_ratings,
                self.five_star_ratings,
            ],
            "liked_percent": self.liked_percent,
            "cover_img": self.cover_img,
            "bbe_score": self.bbe_score,
            "bbe_votes": self.bbe_votes,
            "authors": [author.name for author in self.authors],
            "genres": [genre.name for genre in self.genres],
            "characters": [char.name for char in self.characters],
            "awards": [award.name for award in self.awards],
            "settings": [setting.name for setting in self.settings],
            "publisher": self.publisher.name if self.publisher else "",
            "price": self.price,
        }

    def __repr__(self):
        return f"<Book {self.title} by {self.authors}>"


class User(db.Model, UserMixin, PaginatedAPIMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(128), index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(sa.String(256))
    date_created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    pp: Mapped[str] = mapped_column(sa.String(256), default="uploads/pp/book.png")

    comments: WriteOnlyMapped["Comment"] = relationship(
        back_populates="user", lazy="dynamic"
    )
    book_statuses: Mapped[list["BookStatus"]] = relationship(
        back_populates="user", lazy="dynamic"
    )
    favorite_books: Mapped[list["Book"]] = relationship(
        secondary="user_favorites", overlaps="favorited_by", lazy="dynamic"
    )

    def get_id(self):
        return self.id

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            ph.verify(self.password_hash, password)
            return True
        except VerifyMismatchError:
            return False

    def change_pp(self, filepath):
        self.pp = filepath

    def get_status_for(self, book_id):
        status = db.session.get(BookStatus, (self.id, book_id))
        return status

    def comments_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.comments.select().subquery()
        )
        return db.session.scalar(query)

    def favorite_books_count(self):
        query = sa.select(sa.func.count()).select_from(self.favorite_books.subquery())
        return db.session.scalar(query)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "date_created": self.date_created.replace(tzinfo=timezone.utc).isoformat(),
            "comment_count": self.comments_count(),
            "comments_url": url_for("api.get_comment", id=self.id),
            "favorite_count": self.favorite_books_count(),
            "_links": {"self": url_for("api.get_user", id=self.id)},
            # "pp": self.pp, # useless since the profile picture is not a url but rather a filepath
        }

    def __repr__(self):
        return f"<User {self.id} {self.username}>"


class Comment(db.Model, PaginatedAPIMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column()
    date_created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    book: Mapped[Book] = relationship(back_populates="comments")
    book_id: Mapped[str] = mapped_column(db.ForeignKey(Book.id))

    user: Mapped[User] = relationship(back_populates="comments")
    user_id: Mapped[int] = mapped_column(db.ForeignKey(User.id), index=True)

    def date_created_fmt(self, fmt):
        return self.date_created.strftime(fmt)

    def to_dict(self):
        return {
            "id": self.id,
            "comment": self.body,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "date_created": self.date_created.replace(tzinfo=timezone.utc).isoformat(),
            "_links": {
                "self": url_for("api.get_comment", id=self.id),
                "user": url_for("api.get_user", id=self.user_id),
                "book": url_for("api.get_book", id=self.book_id),
            },
        }

    @staticmethod
    def from_dict(data):
        return Comment(
            body=data["body"],
            user_id=data["user_id"],
            book_id=data["book_id"],
        )

    def __repr__(self):
        return f'<Comment {self.id} "{self.body}">'


class ReadingStatus(db.Model):
    __tablename__ = "reading_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(128), unique=True)

    book_statuses: Mapped[list["BookStatus"]] = relationship(
        back_populates="reading_status", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Reading Status {self.id} '{self.name}'>"


class BookStatus(db.Model):
    __tablename__ = "book_statuses"

    user_id: Mapped[int] = mapped_column(
        db.ForeignKey(User.id), primary_key=True, autoincrement=False
    )
    book_id: Mapped[int] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )
    reading_status_id: Mapped[int] = mapped_column(db.ForeignKey(ReadingStatus.id))
    finished_chapters: Mapped[int] = mapped_column(default=0)

    reading_status: Mapped[ReadingStatus] = relationship(back_populates="book_statuses")
    user: Mapped[User] = relationship(back_populates="book_statuses")
    book: Mapped[Book] = relationship(back_populates="book_statuses")

    def __repr__(self):
        return f"<BookStatus {self.user}, {self.book}, {self.reading_status}, {self.finished_chapters}>"


class UserFavorite(db.Model):
    __tablename__ = "user_favorites"

    user_id: Mapped[int] = mapped_column(
        db.ForeignKey(User.id), primary_key=True, autoincrement=False, index=True
    )
    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False, index=True
    )

    def __repr__(self):
        return f"<UserFavorite {self.user.id} {self.book.id}>"


class Author(db.Model):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)

    books: Mapped[list["Book"]] = relationship(
        back_populates="authors", secondary="book_authors", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Author {self.id} {self.name}>"


class Character(db.Model):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)

    books: Mapped[list["Book"]] = relationship(
        back_populates="characters", secondary="book_characters", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Character {self.id} {self.name}>"


class Genre(db.Model):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)

    books: Mapped[list["Book"]] = relationship(
        back_populates="genres", secondary="book_genres", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Genre {self.id} {self.name}>"


class Award(db.Model):
    __tablename__ = "awards"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)

    books: Mapped[list["Book"]] = relationship(
        back_populates="awards", secondary="book_awards"
    )

    def __repr__(self):
        return f"<Award {self.id} {self.name}>"


class Publisher(db.Model):
    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)

    books: Mapped[list["Book"]] = relationship(
        back_populates="publisher", secondary="book_publisher", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Publisher {self.id} {self.name}>"


class Setting(db.Model):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)

    books: Mapped[list["Book"]] = relationship(
        back_populates="settings", secondary="book_settings", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Setting {self.id} {self.name}>"


class BookAuthor(db.Model):
    __tablename__ = "book_authors"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False, index=True
    )
    author_id: Mapped[int] = mapped_column(
        db.ForeignKey(Author.id), primary_key=True, autoincrement=False, index=True
    )

    def __repr__(self):
        return f"<BookAuthor {self.book_id} {self.author_id}>"


class BookGenre(db.Model):
    __tablename__ = "book_genres"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False, index=True
    )
    genre_id: Mapped[int] = mapped_column(
        db.ForeignKey(Genre.id), primary_key=True, autoincrement=False, index=True
    )

    def __repr__(self):
        return f"<BookGenre {self.book_id} {self.genre_id}>"


class BookCharacter(db.Model):
    __tablename__ = "book_characters"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False, index=True
    )
    character_id: Mapped[int] = mapped_column(
        db.ForeignKey(Character.id), primary_key=True, autoincrement=False, index=True
    )


class BookAward(db.Model):
    __tablename__ = "book_awards"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False, index=True
    )
    award_id: Mapped[int] = mapped_column(
        db.ForeignKey(Award.id), primary_key=True, autoincrement=False, index=True
    )


class BookPublisher(db.Model):
    __tablename__ = "book_publisher"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False, index=True
    )
    publisher_id: Mapped[int] = mapped_column(
        db.ForeignKey(Publisher.id),
        primary_key=True,
        autoincrement=False,
        index=True,
    )


class BookSetting(db.Model):
    __tablename__ = "book_settings"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False, index=True
    )
    setting_id: Mapped[int] = mapped_column(
        db.ForeignKey(Setting.id), primary_key=True, autoincrement=False, index=True
    )


# ! These mappings are used to dynamically create elements in the webpage
# ! as well as apply verification and filtering when querying data.

SEARCHABLE_SCALAR_FIELDS: dict[str, dict[str, str]] = {
    "title": {"label": "Title"},
    "isbn": {"label": "ISBN"},
    "series": {"label": "Series"},
}
"""Mapping for various searchable string attributes of the Book model.\\
Keys are the field names on the Book moel.

```python
SEARCHABLE_SCALAR_FIELDS: dict[str, dict[str, str]] = {
    "title": {"label": "Title"},
    "isbn": {"label": "ISBN"},
    "series": {"label": "Series"},
}

for name, info in SEARCHABLE_SCALAR_FIELDS.items():
    field = getattr(Book, "field")
    label = info["label"]
    # do something with the field name and label
}
```
"""


SEARCHABLE_RELATIONSHIP_FIELDS: dict[str, dict[str, str]] = {
    "authors": {
        "label": "Authors",
        "related_model": "Author",
        "related_field": "name",
    },
    "genres": {
        "label": "Genres",
        "related_model": "Genre",
        "related_field": "name",
    },
    "publisher": {
        "label": "Publisher",
        "related_model": "Publisher",
        "related_field": "name",
    },
    "characters": {
        "label": "Characters",
        "related_model": "Character",
        "related_field": "name",
    },
}
"""
Mapping of various searchable book attributes added as a relationship with other tables.\\
Might restructure into some list of dictionaries to support multuple related field per relationship,\\
i.e. `author.name` and `author.biography`.

```python
SEARCHABLE_RELATIONSHIP_FIELDS = {
    "authors": {
        "label": "Authors",
        "related_model": "Author",
        "related_field": "name",
    },
    "genres": {
        "label": "Genres",
        "related_model": "Genre",
        "related_field": "name",
    },
    "publisher": {
        "label": "Publisher",
        "related_model": "Publisher",
        "related_field": "name",
    },
    "characters": {
        "label": "Characters",
        "related_model": "Character",
        "related_field": "name",
    },
}

# Example usage:
for name, rel_info in SEARCHABLE_RELATIONSHIP_FIELDS.items():
    field = getattr(Book, name)
    related_model = getmodel(rel_info["related_model"]]
    related_field = getattr(related_model, rel_info["related_field"])
    label = rel_info["label"]
    # do something with the book field, related model and field, and label
```
"""


SEARCHABLE_FIELDS = SEARCHABLE_SCALAR_FIELDS | SEARCHABLE_RELATIONSHIP_FIELDS
CATALOGUES = SEARCHABLE_RELATIONSHIP_FIELDS.copy()


SORTABLE_FIELDS: dict[str, dict[str, dict[str]]] = {
    "Book": {
        "bbe_score": {"label": "Score"},
        "title": {"label": "Title"},
        "price": {"label": "Price"},
        "publish_date": {"label": "Publish Date"},
        "num_ratings": {"label": "Rating Count"},
        "pages": {"label": "Page Count"},
        # "publish_date": {"label": "Publish Date"},
    }
}
"""
Mapping of fields per model that can be used to sort query results.\\
Only scalar fields are sortable becuase it makes no sense to sort iterable fields.

```python
SORTABLE_FIELDS: = {
    "Book": {
        "bbe_score": {"label": "Score"},
        "title": {"label": "Title"},
        "price": {"label": "Price"},
        "num_ratings": {"label": "Rating Count"},
        "pages": {"label": "Page Count"},
    }
}

# Example usage:
for model_name, fields in SORTABLE_FIELDS.items():
    model = getmodel(model_name)
    for field_name, info in fields.items():
        field = getattr(model, field_name)
        label = info["label"]
        # do something with the field name and label
```
"""


def getmodel(model_name: str) -> Type[Model]:
    """Get the model class by its name."""
    model = globals().get(model_name)
    if model is None:
        raise ValueError(f"Model {model_name} not found.")
    return model
