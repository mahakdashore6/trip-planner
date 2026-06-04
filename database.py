import sqlite3

def get_db_connection():
    conn = sqlite3.connect('project.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            trip_name TEXT NOT NULL,
            destination TEXT NOT NULL,
            budget INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            category TEXT,
            amount INTEGER,
            description TEXT,
            FOREIGN KEY (trip_id) REFERENCES trips (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(name, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def create_new_trip(user_id, trip_name, destination, budget):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO trips (user_id, trip_name, destination, budget) VALUES (?, ?, ?, ?)', 
                   (user_id, trip_name, destination, budget))
    conn.commit()
    conn.close()

def get_user_trips(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    trips = cursor.execute('SELECT * FROM trips WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return trips

def insert_expense(trip_id, category, amount, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (trip_id, category, amount, description) VALUES (?, ?, ?, ?)', 
                   (trip_id, category, amount, description))
    conn.commit()
    conn.close()