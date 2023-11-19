CREATE TABLE user_categories (
    user_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (user_id, category_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES category(id)
);