CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount FLOAT NOT NULL,
    time_inserted DATE DEFAULT CURRENT_DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
