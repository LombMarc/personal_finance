CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount FLOAT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);