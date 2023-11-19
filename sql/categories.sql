CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    category TEXT NOT NULL
);

-- default category:

INSERT INTO categories (category) VALUES
    ('Paycheck'),
    ('Bonus'),
    ('Grocery'),
    ('Fun'),
    ('Bills'),
    ('Taxes');
