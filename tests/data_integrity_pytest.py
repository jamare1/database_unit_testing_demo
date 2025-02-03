import sqlite3
import pytest

# Set up a test database in memory to test data integrity constraints 

@pytest.fixture  # Pytest's way to set up and teardown a resource, in this case a database connection
def db_connection():
    conn = sqlite3.connect(":memory:")  # Creates an in-memory database
    conn.execute("PRAGMA foreign_keys = ON;")  # Enables foreign key constraints
    cursor = conn.cursor()  # Create a cursor object to execute SQL queries

    # Create tables with different constraints
    cursor.execute("""CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL)""")
    cursor.execute("""CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, total_amount REAL NOT NULL CHECK (total_amount >= 0), 
                   FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE)""")
    conn.commit()  # Commits the changes to the database

    yield conn  # Provide the connection to test the function, also the keyword to differentiate setup and teardown (setup above, teardown below)
    
    conn.close()  # Close the connection after each test function is done


# Test Primary Key Constraint
# @pytest.mark.run(order=1)
def test_primary_key_constraint(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO users (username, email) VALUES ('user1', 'user1@example.com')")
    db_connection.commit()

    with pytest.raises(sqlite3.IntegrityError):  # Primary key should auto-increment, so no duplicate IDs
        cursor.execute("INSERT INTO users (id, username, email) VALUES (1, 'user2', 'user2@example.com')")
        db_connection.commit()


# Test Foreign Key Constraint
# @pytest.mark.run(order=2)
def test_foreign_key_constraint(db_connection):
    cursor = db_connection.cursor()
    with pytest.raises(sqlite3.IntegrityError):  # Foreign key should prevent inserting invalid user_id
        cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (999, 100.0)")  # No user with id=999
        db_connection.commit()


# Test Unique Constraint
# @pytest.mark.run(order=3)
def test_unique_constraint(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO users (username, email) VALUES ('unique_user', 'unique@example.com')")
    db_connection.commit()

    with pytest.raises(sqlite3.IntegrityError):  # Trying to insert a duplicate username
        cursor.execute("INSERT INTO users (username, email) VALUES ('unique_user', 'another@example.com')")
        db_connection.commit()

# Test Non-Null Constraint
# @pytest.mark.run(order=4)
def test_not_null_constraint(db_connection):
    cursor = db_connection.cursor()
    with pytest.raises(sqlite3.IntegrityError):  # Trying to insert NULL into username
        cursor.execute("INSERT INTO users (username, email) VALUES (NULL, 'null_email@example.com')")
        db_connection.commit()

    with pytest.raises(sqlite3.IntegrityError):  # Trying to insert NULL into email
        cursor.execute("INSERT INTO users (username, email) VALUES ('null_username', NULL)")
        db_connection.commit()


# Test Check Constraint
# @pytest.mark.run(order=5)
def test_check_constraint(db_connection):
    cursor = db_connection.cursor()
    with pytest.raises(sqlite3.IntegrityError):  # total_amount should be non-negative
        cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (1, -50.0)")
        db_connection.commit()

"""
def test_example_will_work():
    assert 1 + 1 == 2

def test_example_will_fail():
    assert 1 + 1 == 3
"""

# Run the tests
if __name__ == "__main__":
    pytest.main(["-v", __file__])  # Run pytest with verbose output for this file

