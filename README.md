# Ceramic Store Backend

This is a simple Flask backend for a ceramic store.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the database:
   ```bash
   python database_setup.py
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## API Endpoints

- `GET /api/ceramics`: Returns a list of all ceramic items.
- `GET /api/ceramics/<id>`: Returns a single ceramic item by its ID.
- `GET /api/artists/featured`: Returns the featured artist.

## Testing

This project uses `pytest` for unit testing.

1.  **Install test dependencies**:
    If you haven't already, ensure `pytest` is installed by running:
    ```bash
    pip install pytest
    # Alternatively, if it's included in requirements.txt (which it should be for projects)
    # pip install -r requirements.txt 
    ```
    (Note: `pytest` has been added to `requirements.txt` as part of this setup)

2.  **Run tests**:
    Navigate to the project root directory in your terminal and run:
    ```bash
    pytest
    ```
    This will automatically discover and run the tests in `test_app.py`.
