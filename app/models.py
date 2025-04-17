from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from argon2.exceptions import VerifyMismatchError
from flask_login import UserMixin
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


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    series: Mapped[Optional[str]] = mapped_column()
    rating: Mapped[float] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    language: Mapped[str] = mapped_column()
    isbn: Mapped[str] = mapped_column()
    book_format: Mapped[Optional[str]] = mapped_column()
    edition: Mapped[Optional[str]] = mapped_column()
    pages: Mapped[Optional[int]] = mapped_column()
    publish_date: Mapped[Optional[str]] = mapped_column()
    first_publish_date: Mapped[Optional[str]] = mapped_column()
    num_ratings: Mapped[int] = mapped_column()
    ratings_by_stars: Mapped[str] = mapped_column()
    liked_percent: Mapped[float] = mapped_column()
    setting: Mapped[str] = mapped_column()
    cover_img: Mapped[str] = mapped_column()
    bbe_score: Mapped[int] = mapped_column()
    bbe_votes: Mapped[int] = mapped_column()
    price: Mapped[Optional[float]] = mapped_column()

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

    publisher: Mapped["Publisher"] = relationship(
        back_populates="books", secondary="book_publisher"
    )
    comments: DynamicMapped[list["Comment"]] = relationship(back_populates="book")
    favorited_by: Mapped[list["User"]] = relationship(secondary="user_favorites")
    book_statuses: WriteOnlyMapped[list["BookStatus"]] = relationship(
        back_populates="book", lazy="dynamic"
    )

    def get_status_for(self, user_id):
        if user_id:
            print(f"{user_id=}, {self.id=}")
            status = db.session.get(BookStatus, (user_id, self.id))
            return status
        else:
            return None

    def __repr__(self):
        return f"<Book {self.title} by {self.authors}>"


class User(db.Model, UserMixin):
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

    def get_book_status(self, book_id):
        status = db.session.get(BookStatus, (self.id, book_id))
        return status

    def __repr__(self):
        return f"<User {self.id} {self.username}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str] = mapped_column()
    date_created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    book: Mapped[Book] = relationship(back_populates="comments")
    book_id: Mapped[str] = mapped_column(db.ForeignKey(Book.id))

    user: Mapped[User] = relationship(back_populates="comments")
    user_id: Mapped[int] = mapped_column(db.ForeignKey(User.id), index=True)

    def __repr__(self):
        return f'<Comment {self.id} "{self.comment}">'

    def date_created_fmt(self, fmt):
        return self.date_created.strftime(fmt)


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
        db.ForeignKey(User.id), primary_key=True, autoincrement=False
    )
    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )

    def __repr__(self):
        return f"<UserFavorite {self.user.id} {self.book.id}"


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


class BookAuthor(db.Model):
    __tablename__ = "book_authors"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )
    author_id: Mapped[int] = mapped_column(
        db.ForeignKey(Author.id), primary_key=True, autoincrement=False
    )

    def __repr__(self):
        return f"<BookAuthor {self.book_id} {self.author_id}>"


class BookGenre(db.Model):
    __tablename__ = "book_genres"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )
    genre_id: Mapped[int] = mapped_column(
        db.ForeignKey(Genre.id), primary_key=True, autoincrement=False
    )

    def __repr__(self):
        return f"<BookGenre {self.book_id} {self.genre_id}>"


class BookCharacter(db.Model):
    __tablename__ = "book_characters"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )
    character_id: Mapped[int] = mapped_column(
        db.ForeignKey(Character.id), primary_key=True, autoincrement=False
    )


class BookAward(db.Model):
    __tablename__ = "book_awards"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )
    award_id: Mapped[int] = mapped_column(
        db.ForeignKey(Award.id), primary_key=True, autoincrement=False
    )


class BookPublisher(db.Model):
    __tablename__ = "book_publisher"

    book_id: Mapped[str] = mapped_column(
        db.ForeignKey(Book.id), primary_key=True, autoincrement=False
    )
    publisher_id: Mapped[int] = mapped_column(
        db.ForeignKey("publishers.id"), primary_key=True, autoincrement=False
    )
