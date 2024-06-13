CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 10000.00);

CREATE UNIQUE INDEX username ON users (username);

CREATE TABLE stocks(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    symbol TEXT NOT NULL);

CREATE TABLE portfolio(
    shares NUMERIC NOT NULL,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(stock_id) REFERENCES stocks(id));

CREATE TABLE history(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    order_type INTEGER NOT NULL,
    shares INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    time_stamp TEXT,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(stock_id) REFERENCES stocks(id));
