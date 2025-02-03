import sqlite3
import unittest

class TestDataIntegrity(unittest.TestCase):

    # Set up a test database in memory to test data integrity constraints 
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")  # Creates an in-memory database
        self.conn.execute("PRAGMA foreign_keys = ON;")  # Enables foreign key constraints
        self.cursor = self.conn.cursor()  # Create a cursor object to execute SQL queries

        # Create tables with different constraints
        self.cursor.execute("""CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL)""")
        self.cursor.execute("""CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, total_amount REAL NOT NULL CHECK (total_amount >= 0), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)""")
        self.conn.commit()  # Commits the changes to the database

    # Close the database connection after each test
    def tearDown(self):
        self.conn.close()

    # Test Primary Key Constraint
    def test_primary_key_constraint(self):
        self.cursor.execute("INSERT INTO users (username, email) VALUES ('user1', 'user1@example.com')")
        self.conn.commit()

        # Attempt to insert a duplicate ID manually (should fail)
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO users (id, username, email) VALUES (1, 'user2', 'user2@example.com')")
            self.conn.commit()

    # Test Foreign Key Constraint
    def test_foreign_key_constraint(self):
        # Try to insert an order with a non-existent user_id (should fail)
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (999, 100.0)")
            self.conn.commit()

    # Test Unique Constraint
    def test_unique_constraint(self):
        self.cursor.execute("INSERT INTO users (username, email) VALUES ('unique_user', 'unique@example.com')")
        self.conn.commit()

        # Attempt to insert a duplicate username (should fail)
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO users (username, email) VALUES ('unique_user', 'another@example.com')")
            self.conn.commit()

    # Test Non-Null Constraint
    def test_not_null_constraint(self):
        # Attempt to insert a NULL username (should fail)
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO users (username, email) VALUES (NULL, 'null_email@example.com')")
            self.conn.commit()

        # Attempt to insert a NULL email (should fail)
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO users (username, email) VALUES ('null_username', NULL)")
            self.conn.commit()

    # Test Check Constraint
    def test_check_constraint(self):
        # Insert a user first (needed for foreign key constraint)
        self.cursor.execute("INSERT INTO users (username, email) VALUES ('valid_user', 'valid@example.com')")
        self.conn.commit()

        # Attempt to insert an order with a negative total_amount (should fail)
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (1, -50.0)")
            self.conn.commit()

    def test_check_will_fail(self):
        assert 1 + 1 == 3

# Run the tests
if __name__ == "__main__":
    unittest.main(verbosity = 2)
