import sqlite3

def setup_database():
    conn = sqlite3.connect('ceramics.db')
    cursor = conn.cursor()

    # Create artists table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        image_url TEXT,
        is_featured BOOLEAN DEFAULT 0
    )
    ''')

    # Create ceramics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ceramics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        image_url TEXT,
        description TEXT,
        category TEXT CHECK(category IN ('new-arrival', 'best-seller', 'regular')),
        artist_id INTEGER,
        FOREIGN KEY (artist_id) REFERENCES artists(id)
    )
    ''')

    # Insert sample artists
    sample_artists = [
        ('John Doe', 'https://example.com/john_doe.jpg', 1),
        ('Jane Smith', 'https://example.com/jane_smith.jpg', 0),
        ('Artisan Potter', 'https://example.com/artisan_potter.jpg', 0)
    ]
    cursor.executemany('INSERT INTO artists (name, image_url, is_featured) VALUES (?, ?, ?)', sample_artists)

    # Insert sample ceramics
    sample_ceramics = [
        ('Elegant Mug', 18.99, 'https://example.com/elegant_mug.jpg', 'A beautifully handcrafted elegant mug.', 'new-arrival', 1),
        ('Rustic Plate', 28.50, 'https://example.com/rustic_plate.jpg', 'A decorative rustic ceramic plate.', 'best-seller', 2),
        ('Modern Vase', 55.00, 'https://example.com/modern_vase.jpg', 'A sleek modern vase for your home.', 'new-arrival', 1),
        ('Serving Bowl', 35.75, 'https://example.com/serving_bowl.jpg', 'Large ceramic serving bowl.', 'regular', 2),
        ('Tea Pot', 42.00, 'https://example.com/tea_pot.jpg', 'Handmade ceramic tea pot.', 'best-seller', 3),
        ('Small Planter', 22.00, 'https://example.com/small_planter.jpg', 'A small planter for your succulents.', 'regular', 1)
    ]
    cursor.executemany('INSERT INTO ceramics (name, price, image_url, description, category, artist_id) VALUES (?, ?, ?, ?, ?, ?)', sample_ceramics)

    conn.commit()
    conn.close()
    print("Database ceramics.db created and populated successfully.")

if __name__ == '__main__':
    setup_database()
