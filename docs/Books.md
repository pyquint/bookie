# `books` schema
```sql
CREATE TABLE books (
        id VARCHAR NOT NULL,
        title VARCHAR NOT NULL,
        series VARCHAR,
        description VARCHAR,
        language VARCHAR NOT NULL,
        isbn VARCHAR NOT NULL,
        book_format VARCHAR,
        edition VARCHAR,
        publish_date VARCHAR,
        first_publish_date VARCHAR,
        five_star_ratings INTEGER NOT NULL,
        four_star_ratings INTEGER NOT NULL,
        three_star_ratings INTEGER NOT NULL,
        two_star_ratings INTEGER NOT NULL,
        one_star_ratings INTEGER NOT NULL,
        cover_img VARCHAR NOT NULL,
        rating FLOAT NOT NULL,
        pages INTEGER,
        num_ratings INTEGER NOT NULL,
        liked_percent FLOAT,
        bbe_score INTEGER NOT NULL,
        bbe_votes INTEGER NOT NULL,
        price FLOAT,
        CONSTRAINT pk_books PRIMARY KEY (id)
);
```

# `Books` model
```python
class Book(db.Model, PaginatedAPIMixin):
    __tablename__ = "books"

    # column attributes
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    isbn: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column()
    book_format: Mapped[str] = mapped_column()
    language: Mapped[str] = mapped_column()
    series: Mapped[str] = mapped_column()
    edition: Mapped[str] = mapped_column()
    cover_img: Mapped[str] = mapped_column()

    # measurement of book ranking
    rating: Mapped[float] = mapped_column(index=True)
    num_ratings: Mapped[int] = mapped_column(index=True)
    bbe_score: Mapped[int] = mapped_column()
    bbe_votes: Mapped[int] = mapped_column()

    # split from `num_ratings` column
    five_star_ratings: Mapped[int] = mapped_column()
    four_star_ratings: Mapped[int] = mapped_column()
    three_star_ratings: Mapped[int] = mapped_column()
    two_star_ratings: Mapped[int] = mapped_column()
    one_star_ratings: Mapped[int] = mapped_column()

    # either empty or invalid during import
    pages: Mapped[Optional[int]] = mapped_column()
    price: Mapped[Optional[float]] = mapped_column()
    liked_percent: Mapped[Optional[float]] = mapped_column()

    # datetime
    publish_date: Mapped[Optional[datetime]] = mapped_column()
    publish_date_format: Mapped[Optional[str]] = mapped_column()
    first_publish_date: Mapped[Optional[datetime]] = mapped_column()
    first_publish_date_format: Mapped[Optional[str]] = mapped_column()

    # relationship attributes
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

    # relationship attributes related to users
    comments: DynamicMapped[list["Comment"]] = relationship(back_populates="book")
    favorited_by: Mapped[list["User"]] = relationship(secondary="user_favorites")
    book_statuses: WriteOnlyMapped[list["BookStatus"]] = relationship(
        back_populates="book", lazy="dynamic"
    )
```
