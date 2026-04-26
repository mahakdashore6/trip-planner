from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'mahak_secret_key'

# --- DATABASE CONNECTION ---
def get_db_connection():
    conn = sqlite3.connect('trip_planner.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login_logic', methods=['POST'])
def login_logic():
    email = request.form.get('email')
    password = request.form.get('password')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
    conn.close()
    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return redirect(url_for('dashboard'))
    return "Invalid Credentials! <a href='/login'>Try again</a>"

@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/register_logic', methods=['POST'])
def register_logic():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login_page'))
    except:
        return "Email already exists! <a href='/register_page'>Try again</a>"

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        conn = get_db_connection()
        trips_rows = conn.execute('SELECT * FROM trips WHERE user_id = ?', (session['user_id'],)).fetchall()
        trips = []
        for row in trips_rows:
            trip = dict(row)
            expenses = conn.execute('SELECT * FROM expenses WHERE trip_id = ?', (trip['id'],)).fetchall()
            trip['expenses'] = expenses
            total_spent = sum(exp['amount'] for exp in expenses)
            trip['total_spent'] = total_spent
            trip['remaining'] = trip['budget'] - total_spent
            trip['plans'] = conn.execute('SELECT * FROM itinerary WHERE trip_id = ?', (trip['id'],)).fetchall()
            trips.append(trip)
        conn.close()
        return render_template('dashboard.html', name=session['user_name'], trips=trips)
    return redirect(url_for('login_page'))

@app.route('/add_trip', methods=['POST'])
def add_trip():
    if 'user_id' in session:
        conn = get_db_connection()
        conn.execute('INSERT INTO trips (user_id, trip_name, destination, start_date, budget) VALUES (?, ?, ?, ?, ?)',
                     (session['user_id'], request.form.get('trip_name'), request.form.get('destination'), request.form.get('start_date'), request.form.get('budget')))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/add_expense/<int:trip_id>', methods=['POST'])
def add_expense(trip_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO expenses (trip_id, category, amount, description) VALUES (?, ?, ?, ?)',
                 (trip_id, request.form.get('category'), request.form.get('amount'), request.form.get('description')))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/add_plan/<int:trip_id>', methods=['POST'])
def add_plan(trip_id):
    conn = get_db_connection()
    conn.execute('INSERT INTO itinerary (trip_id, day_number, activity) VALUES (?, ?, ?)',
                 (trip_id, request.form.get('day_number'), request.form.get('activity')))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    return redirect(url_for('dashboard'))

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/delete_trip/<int:trip_id>')
def delete_trip(trip_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)