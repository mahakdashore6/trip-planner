import sqlite3

def create_tables():
    conn = sqlite3.connect('trip_planner.db')
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT)''')

    # 2. Trips Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS trips 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, trip_name TEXT, 
                    destination TEXT, start_date DATE, budget REAL)''')

    # 3. Expenses Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, trip_id INTEGER, category TEXT, 
                    amount REAL, description TEXT)''')

    # 4. Itinerary Table (Point 4: Day-wise Planning ke liye)
    # Ise naya add kiya gaya hai
    cursor.execute('''CREATE TABLE IF NOT EXISTS itinerary 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, trip_id INTEGER, day_number TEXT, 
                    activity TEXT, FOREIGN KEY (trip_id) REFERENCES trips (id))''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database ready with Planning table!")