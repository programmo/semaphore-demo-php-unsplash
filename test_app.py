import pytest
import os
import tempfile
import json
from app import app as flask_app # Import the Flask app instance
from database_setup import setup_database

# Fixture to set up a temporary database and test client
@pytest.fixture
def client():
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db', prefix='test_ceramics_')
    flask_app.config['DATABASE'] = db_path
    flask_app.config['TESTING'] = True

    # Store the original DATABASE path from app.py to restore later
    original_db_path = flask_app.DATABASE
    flask_app.DATABASE = db_path # Override DATABASE path in app.py for query_db

    # Initialize the temporary database with schema and sample data
    # We need to ensure setup_database uses the db_path
    # For simplicity, we'll temporarily modify the global DATABASE variable in database_setup.py
    # This is not ideal but avoids complex refactoring of database_setup.py for this task
    
    original_setup_db_name = 'ceramics.db' # default in database_setup
    if os.path.exists(original_setup_db_name): # if a real db exists, rename it temporarily
        os.rename(original_setup_db_name, original_setup_db_name + ".bak_for_test")

    # Temporarily change directory to where database_setup.py expects to create the db
    # or modify database_setup.py to accept a path (preferred but more changes)
    # For now, let's assume database_setup.py creates 'ceramics.db' in current dir
    # We will rename our temp db to 'ceramics.db' for setup, then rename it back
    
    # Simplification: Assume database_setup.py uses the flask_app.DATABASE global if available,
    # or modify it to accept a path. For now, let's make it use the flask_app.DATABASE
    # No, database_setup.py has its own connect string.
    # The easiest way is to ensure 'ceramics.db' is created as the temp one.
    
    # Use a context manager for the database connection in setup_database
    # to ensure it's closed before flask_app uses it.
    # For now, let's directly call setup_database and it will create 'ceramics.db'
    # We must ensure it creates our temporary db_path
    
    # Let's modify database_setup.py to accept a database_name parameter.
    # This is too complex for this agent.
    # The current database_setup.py hardcodes 'ceramics.db'.
    # So, we'll create our temp db, then copy its contents to 'ceramics.db' for setup,
    # then copy back. This is also not good.

    # Alternative: use monkeypatching for sqlite3.connect in database_setup
    # For now, the simplest is to ensure that when setup_database() is called,
    # it writes to our temporary db_path.
    # We will rename our temporary db_path to 'ceramics.db' before calling setup_database,
    # and then rename it back to db_path after setup.

    temp_db_target_name = 'ceramics.db' # The name database_setup.py will use
    
    # If 'ceramics.db' (the target for setup_database) exists, back it up
    real_db_existed = False
    if os.path.exists(temp_db_target_name):
        real_db_existed = True
        os.rename(temp_db_target_name, temp_db_target_name + ".real_backup")

    # Rename our temporary file to 'ceramics.db' so setup_database writes into it
    os.close(db_fd) # Close the file descriptor from mkstemp
    os.rename(db_path, temp_db_target_name) # db_path is now named 'ceramics.db'
    
    setup_database() # This will create and populate 'ceramics.db' (which is our temp file)

    # Rename 'ceramics.db' back to its unique temporary name (db_path)
    os.rename(temp_db_target_name, db_path)

    # Restore the original 'ceramics.db' if it was backed up
    if real_db_existed:
        os.rename(temp_db_target_name + ".real_backup", temp_db_target_name)


    with flask_app.test_client() as client:
        with flask_app.app_context():
            # get_db() in app.py will now use flask_app.config['DATABASE']
            pass
        yield client

    # Teardown: restore original DB path in app and delete temporary database
    flask_app.DATABASE = original_db_path
    os.unlink(db_path) # Delete the temporary database file
    
    if os.path.exists(original_setup_db_name + ".bak_for_test"):
         os.rename(original_setup_db_name + ".bak_for_test", original_setup_db_name)


# --- Test Cases for /api/ceramics ---

def test_get_all_ceramics(client):
    """Test successful retrieval of all ceramics."""
    response = client.get('/api/ceramics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 6 # Based on sample data in database_setup.py

def test_get_ceramics_category_new_arrival(client):
    """Test ?category=new-arrival filtering."""
    response = client.get('/api/ceramics?category=new-arrival')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0 # Expect some new arrivals
    for item in data:
        assert item['category'] == 'new-arrival'
    # Specifically, database_setup.py has 2 new-arrivals
    assert len(data) == 2 


def test_get_ceramics_category_best_seller(client):
    """Test ?category=best-seller filtering."""
    response = client.get('/api/ceramics?category=best-seller')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0 # Expect some best sellers
    for item in data:
        assert item['category'] == 'best-seller'
    # Specifically, database_setup.py has 2 best-sellers
    assert len(data) == 2

def test_get_ceramics_search_name(client):
    """Test ?search=<query> filtering by name."""
    response = client.get('/api/ceramics?search=Mug')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['name'] == 'Elegant Mug'

def test_get_ceramics_search_description(client):
    """Test ?search=<query> filtering by description."""
    response = client.get('/api/ceramics?search=handcrafted') # "Elegant Mug" is handcrafted
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['name'] == 'Elegant Mug'

def test_get_ceramics_category_and_search(client):
    """Test with a combination of category and search."""
    # 'Elegant Mug' is 'new-arrival' and has 'Elegant' in its name
    response = client.get('/api/ceramics?category=new-arrival&search=Elegant')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == 'Elegant Mug'
    assert data[0]['category'] == 'new-arrival'

def test_get_ceramics_unknown_category(client):
    """Test with an unknown category (should return an empty list)."""
    response = client.get('/api/ceramics?category=unknown-category')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_ceramics_search_no_results(client):
    """Test with a search query that yields no results."""
    response = client.get('/api/ceramics?search=NonExistentQueryString')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

# --- Test Cases for /api/ceramics/<id> ---

def test_get_ceramic_existing_id(client):
    """Test successful retrieval of an existing ceramic item."""
    # Assuming item with ID 1 exists from database_setup.py
    response = client.get('/api/ceramics/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == 1
    assert data['name'] == 'Elegant Mug' # First item from database_setup.py

def test_get_ceramic_non_existent_id(client):
    """Test retrieval of a non-existent ceramic item (should return 404)."""
    response = client.get('/api/ceramics/9999') # Assuming ID 9999 does not exist
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['message'] == 'Ceramic not found'

# --- Test Cases for /api/artists/featured ---

def test_get_featured_artist(client):
    """Test successful retrieval of the featured artist."""
    response = client.get('/api/artists/featured')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['is_featured'] == 1
    assert data['name'] == 'John Doe' # First artist from database_setup.py is featured

def test_get_featured_artist_none_featured(client):
    """Test case where no artist is featured (should return 404)."""
    # To test this, we need to ensure no artist is featured in the test DB.
    # We'll clear the is_featured flag for all artists in the current test DB session.
    # This requires a way to interact with the db within the test,
    # or a specialized setup.
    
    # Simplest way: run an SQL update via the app's db connection if possible,
    # or modify the fixture to allow for specific db states.
    
    # Using the app's get_db within a test context to modify data
    with flask_app.app_context():
        # Correctly get the database connection using the application's get_db()
        from app import get_db as app_get_db 
        conn = app_get_db()
        cursor = conn.cursor()
        # Set all artists to not be featured
        cursor.execute("UPDATE artists SET is_featured = 0")
        conn.commit() # Ensure the change is committed to the database
        # No need to close cursor or connection here if get_db is well-behaved with app_context
        # cursor.close() # Typically not needed if connection is managed by app_context

    response = client.get('/api/artists/featured')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['message'] == 'No featured artist found'

    # Restore: Set John Doe back to featured for other tests if db is reused (it's not per test function here)
    # This is important if tests share the same db setup state across one session.
    # However, the 'client' fixture re-initializes the DB for each test function.
    # So, this modification is isolated to this test.
    # If the DB were shared, we'd do:
    # with flask_app.app_context():
    #   conn = app_get_db()
    #   cursor = conn.cursor()
    #   cursor.execute("UPDATE artists SET is_featured = 1 WHERE name = 'John Doe'")
    #   conn.commit()
    #   cursor.close()

# --- Test to ensure the main app.py DATABASE is restored ---
def test_database_path_restored():
    import app as main_app_module
    assert main_app_module.DATABASE == 'ceramics.db'

# TODO: Consider adding a test for the root path '/' serving index.html
def test_get_index_html(client):
    """Test that the root path serves index.html."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    assert b"<title>Stitch Design</title>" in response.data # Check for a unique element from index.html
    assert b"new-arrivals-container" in response.data # Check for a container id
    assert b"static/js/app.js" in response.data # Check for script include
