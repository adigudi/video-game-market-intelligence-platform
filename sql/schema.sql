DROP TABLE IF EXISTS clusters;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS region_population;

CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    platform TEXT,
    year INTEGER,
    genre TEXT,
    publisher TEXT,
    critic_score REAL,
    user_score REAL,
    rating TEXT
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    na_sales REAL,
    eu_sales REAL,
    jp_sales REAL,
    other_sales REAL,
    global_sales REAL,
    FOREIGN KEY (game_id) REFERENCES games (id)
);

CREATE TABLE region_population (
    year INTEGER PRIMARY KEY,
    na_population REAL,
    eu_population REAL,
    jp_population REAL,
    other_population REAL
);

CREATE TABLE clusters (
    game_id INTEGER PRIMARY KEY,
    cluster_id INTEGER,
    FOREIGN KEY (game_id) REFERENCES games (id)
);
