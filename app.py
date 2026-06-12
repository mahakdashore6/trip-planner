import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from google import genai 
from database import insert_expense, init_db, add_feedback

app = Flask(__name__)
app.secret_key = "mahak_secret_key"

# --- Gemini API Configuration ---
client = genai.Client(api_key="AIzaSyDwIS7pWp2VkeATs0bq7VQO8QxgTFya8r8")

def get_db_connection():
    conn = sqlite3.connect('trip_planner.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Auth & Main Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register_logic', methods=['POST'])
def register_logic():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
        flash("Account successfully created!")
        return redirect(url_for('login_page'))
    except:
        flash("Registration failed. Email might already exist.")
        return redirect(url_for('register_page'))
    finally:
        conn.close()

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
    flash("Wrong email or password!")
    return redirect(url_for('login_page'))

# --- Dashboard & Features ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    conn = get_db_connection()
    trips = conn.execute('SELECT * FROM trips WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', trips=trips)

@app.route('/create_trip', methods=['POST'])
def create_trip():
    trip_name = request.form.get('trip_name')
    dest = request.form.get('destination')
    budget = request.form.get('budget')
    conn = get_db_connection()
    conn.execute('INSERT INTO trips (user_id, trip_name, destination, budget) VALUES (?, ?, ?, ?)',
                 (session['user_id'], trip_name, dest, budget))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    trip_id = request.form.get('trip_id')
    category = request.form.get('category')
    amount = request.form.get('amount')
    description = request.form.get('description')
    insert_expense(trip_id, category, amount, description)
    flash("Expense add ho gaya!")
    return redirect(url_for('dashboard'))

# --- Help & Feedback Routes ---
@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/feedback')
def feedback_page():
    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    comment = request.form.get('comment')
    rating = request.form.get('rating')
    add_feedback(session['user_id'], comment, rating)
    flash("Feedback dene ke liye shukriya! ✨")
    return redirect(url_for('dashboard'))

# --- AI Planning Route ---
@app.route('/guest_search', methods=['POST'])
def ai_plan():
    city = request.form.get('city', '').strip()
    prompt = f"Create a short travel itinerary for {city} with local tips."
    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        raw_text = response.text
    except:
        raw_text = f"### Welcome to {city}! Enjoy your trip."
    
    formatted_text = raw_text.replace("\n", "<br>").replace("**", "<b>").replace("### ", "<h4>")
    city_lower = city.lower()
    image_url = f"https://loremflickr.com/800/400/{city_lower},travel,monument/all"
    return render_template('ai_result.html', info=formatted_text, city=city, image_url=image_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)