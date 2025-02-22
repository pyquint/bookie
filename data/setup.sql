CREATE TABLE IF NOT EXISTS books (
    book_id TEXT PRIMARY KEY,
    title TEXT,
    series TEXT,
    author TEXT,
    rating REAL,
    description TEXT,
    language TEXT,
    isbn TEXT,
    genres TEXT,
    characters TEXT,
    book_format TEXT,
    edition TEXT,
    pages INTEGER,
    publisher TEXT,
    publish_date TEXT,
    first_publish_date TEXT,
    awards TEXT,
    num_ratings REAL,
    ratings_by_stars TEXT,
    liked_percent REAL,
    setting TEXT,
    cover_img TEXT,
    bbe_score REAL,
    bbe_votes INTEGER,
    price REAL
);

CREATE TABLE IF NOT EXISTS users (
    uid INTEGER PRIMARY KEY,
    username TEXT,
    email TEXT,
    date_created TEXT,
    password_hash TEXT,
    PRIMARY KEY
);
