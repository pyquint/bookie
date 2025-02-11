CREATE VIRTUAL TABLE books_fts USING fts5("book_id","title","series","author","rating","description","language","isbn","genres","characters","book_format","edition","pages","publisher","publish_date","first_publish_date","awards","num_ratings","ratings_by_stars","liked_percent","setting","cover_img","bbe_score","bbe_votes","price");

INSERT INTO books_fts("book_id","title","series","author","rating","description","language","isbn","genres","characters","book_format","edition","pages","publisher","publish_date","first_publish_date","awards","num_ratings","ratings_by_stars","liked_percent","setting","cover_img","bbe_score","bbe_votes","price")

SELECT "book_id","title","series","author","rating","description","language","isbn","genres","characters","book_format","edition","pages","publisher","publish_date","first_publish_date","awards","num_ratings","ratings_by_stars","liked_percent","setting","cover_img","bbe_score","bbe_votes","price"
FROM books;
