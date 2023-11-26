CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    category TEXT NOT NULL,
    is_wealth INTEGER DEFAULT 0 NOT NULL  -- BOOL/BIT type is not defined in sqlite3, so use integer between 0 and 1
);

-- default category:

INSERT INTO categories (category) VALUES
    ('Paycheck'),
    ('Bonus'),
    ('Grocery'),
    ('Fun'),
    ('Bills'),
    ('Taxes');
