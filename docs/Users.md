This document defines the implementation of user accounts in the application.

# `users` schema
```sql
CREATE TABLE users (
        id INTEGER NOT NULL,
        username VARCHAR(64) NOT NULL,
        email VARCHAR(128) NOT NULL,
        password_hash VARCHAR(256),
        date_created DATETIME NOT NULL,
        pp VARCHAR(256) NOT NULL,
        CONSTRAINT pk_users PRIMARY KEY (id)
);
CREATE INDEX ix_users_date_created ON users (date_created);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_username ON users (username);
```

# `User` model
```python
class User(db.Model, UserMixin):
    __tablename__ = "users"

    # column attributes
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(128), index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(sa.String(256))
    date_created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    pp: Mapped[str] = mapped_column(sa.String(256), default="uploads/pp/book.png")

    # relationship attributes for comments
    comments: WriteOnlyMapped["Comment"] = relationship(
        back_populates="user", lazy="dynamic"
    )

    # relationship attributes related to book tracking
    book_statuses: Mapped[list["BookStatus"]] = relationship(
        back_populates="user", lazy="dynamic"
    )
    favorite_books: Mapped[list["Book"]] = relationship(
        secondary="user_favorites", overlaps="favorited_by", lazy="dynamic"
    )
```

Sqlite3 does not have a native `DATETIME` data type unlike other SQL RDBMS. However, through SQLAlchemy ORM we can set model object attributes as `datetime` objects, automatically converting them to string values when commiting into the database, and vice versa when querying users from the database using the ORM.

> See also: [SQLite3 Date And Time Functions](https://sqlite.org/lang_datefunc.html)

Currently, user profile pictures stored internally as filepaths relative to the `static` folder.

# Authentication
Password hashing and verification is done with the [argon2-cffi](https://pypi.org/project/argon2-cffi/) package.


```Python
# __init__.py

from argon2 import PasswordHasher

ph = PasswordHasher()
```

```Python
# app\models.py

from app import ph
class User(db.Model, UserMixin):
    ...


    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            ph.verify(self.password_hash, password)
            return True
        except VerifyMismatchError:
            return False
```

> See also: [argon2-cffi API reference](https://argon2-cffi.readthedocs.io/en/stable/api.html)
