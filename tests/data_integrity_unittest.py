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

    def tearDown(self):
        self.conn.close()  # Close the database connection after each test

    # Test Primary Key Constraint
    def test_insertUser_duplicatePrimaryKey_raisesIntegrityError(self):
        self.cursor.execute("INSERT INTO users (username, email) VALUES ('user1', 'user1@example.com')")
        self.conn.commit()

        with self.assertRaises(sqlite3.IntegrityError):  # Attempt to insert a duplicate ID manually
            self.cursor.execute("INSERT INTO users (id, username, email) VALUES (1, 'user2', 'user2@example.com')")
            self.conn.commit()

    # Test Foreign Key Constraint
    def test_insertOrder_invalidUserId_raisesForeignKeyError(self):
        with self.assertRaises(sqlite3.IntegrityError):  # Try to insert an order with a non-existent user_id 
            self.cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (999, 100.0)")
            self.conn.commit()

    # Test Unique Constraint
    def test_insertUser_duplicateUsername_raisesIntegrityError(self):
        self.cursor.execute("INSERT INTO users (username, email) VALUES ('unique_user', 'unique@example.com')")
        self.conn.commit()

        with self.assertRaises(sqlite3.IntegrityError):  # Attempt to insert a duplicate username
            self.cursor.execute("INSERT INTO users (username, email) VALUES ('unique_user', 'another@example.com')")
            self.conn.commit()

    # Test Non-Null Constraint
    def test_insertUser_nullValues_raisesNotNullConstraintError(self):
        with self.assertRaises(sqlite3.IntegrityError):  # Attempt to insert a NULL username
            self.cursor.execute("INSERT INTO users (username, email) VALUES (NULL, 'null_email@example.com')")
            self.conn.commit()

        with self.assertRaises(sqlite3.IntegrityError):  # Attempt to insert a NULL email
            self.cursor.execute("INSERT INTO users (username, email) VALUES ('null_username', NULL)")
            self.conn.commit()

    # Test Check Constraint
    def test_insertOrder_negativeTotalAmount_raisesCheckConstraintError(self):
        self.cursor.execute("INSERT INTO users (username, email) VALUES ('valid_user', 'valid@example.com')")  # Insert a user first (needed for foreign key constraint)
        self.conn.commit()

        with self.assertRaises(sqlite3.IntegrityError):  # Attempt to insert an order with a negative total_amount 
            self.cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (1, -50.0)")
            self.conn.commit()

    def test_check_will_fail(self):
        assert 1 + 1 == 3

# Run the tests
if __name__ == "__main__":
    unittest.main(verbosity = 2)
