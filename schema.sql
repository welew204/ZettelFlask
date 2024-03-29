DROP TABLE IF EXISTS author;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS tpcnx;
DROP TABLE IF EXISTS weights;

CREATE TABLE author (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body_formatted TEXT NOT NULL,
    published TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES author (id) 
);

CREATE TABLE tpcnx (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    user_conf INTEGER,
    weight REAL,
    FOREIGN KEY (tag_id) REFERENCES tags (id),
    FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT NOT NULL,
    best_token TEXT NOT NULL,
    count INTEGER,
    idf REAL
);