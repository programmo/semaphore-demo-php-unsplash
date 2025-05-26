import sqlite3
from flask import Flask, jsonify, request, g, render_template

app = Flask(__name__)
DATABASE = 'ceramics.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # This allows accessing columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    # No commit here, connection is managed by get_db and close_connection
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/api/ceramics', methods=['GET'])
def get_ceramics():
    search_term = request.args.get('search')
    category_filter = request.args.get('category')

    query = "SELECT * FROM ceramics"
    params = []
    conditions = []

    if search_term:
        conditions.append("(name LIKE ? OR description LIKE ?)")
        params.extend([f"%{search_term}%", f"%{search_term}%"])
    
    if category_filter:
        conditions.append("category = ?")
        params.append(category_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    ceramics_rows = query_db(query, params)
    # Ensure rows are not None before creating list of dicts
    ceramics_list = [dict(row) for row in ceramics_rows] if ceramics_rows else []
    return jsonify(ceramics_list)

@app.route('/api/ceramics/<int:id>', methods=['GET'])
def get_ceramic(id):
    ceramic_row = query_db("SELECT * FROM ceramics WHERE id = ?", [id], one=True)
    if ceramic_row:
        return jsonify(dict(ceramic_row))
    return jsonify({"message": "Ceramic not found"}), 404

@app.route('/api/artists/featured', methods=['GET'])
def get_featured_artist():
    artist_row = query_db("SELECT * FROM artists WHERE is_featured = 1", one=True) # In schema, is_featured is BOOLEAN (0 or 1)
    if artist_row:
        return jsonify(dict(artist_row))
    return jsonify({"message": "No featured artist found"}), 404

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Ensure the database is created before running the app
    # In a production environment, you might want to handle this differently
    from database_setup import setup_database
    import os
    if not os.path.exists(DATABASE):
        print(f"Database {DATABASE} not found. Initializing...")
        setup_database()
        print("Database initialized.")
    app.run(debug=True)
