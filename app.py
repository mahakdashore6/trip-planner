import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from google import genai 

app = Flask(__name__)
app.secret_key = "mahak_secret_key"

# --- Gemini API Configuration ---
client = genai.Client(api_key="AIzaSyDwIS7pWp2VkeATs0bq7VQO8QxgTFya8r8")

def get_db_connection():
    conn = sqlite3.connect('trip_planner.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Homepage & Auth Routes ---
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
    conn = get_db_connection()
    conn.execute('INSERT INTO expenses (trip_id, category, amount, description) VALUES (?, ?, ?, ?)',
                  (trip_id, category, amount, description))
    conn.commit()
    conn.close()
    flash("Expense add ho gaya!")
    return redirect(url_for('dashboard'))

# --- AI Planning Route ---
@app.route('/guest_search', methods=['POST'])
def ai_plan():
    city = request.form.get('city', '').strip()
    prompt = f"Create a short travel itinerary for {city} with local tips."
    
    try:
        # 1. Gemini से प्लान लेने की कोशिश करें
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        raw_text = response.text
    except Exception as e:
        # 2. बैकअप प्लान
        print(f"Gemini API Limit reached, using backup for {city}")
        raw_text = f"""
### 📍 Welcome to {city}! 

**Ideal Duration:** 2 Days  
**Best Time to Visit:** October to March  

* **Morning:** Start your day by visiting the historical landmarks and famous central places of {city}. Enjoy a traditional local breakfast.
* **Afternoon:** Explore cultural heritage sites, local markets, and try unique regional street food.
* **Evening:** Spend a relaxing evening at the lakeside, river ghats, or prominent sunset view points of {city}.

### 💡 Local Tips for Travelers:
* Use local transport like auto-rickshaws for easy transit. 
* Don't miss out on trying the authentic local food specialties!
        """

    # 3. फ़ॉर्मेटिंग फिक्स
    formatted_text = raw_text.replace("\n", "<br>")
    formatted_text = formatted_text.replace("**", "<b>")
    formatted_text = formatted_text.replace("### ", "<h4>").replace("## ", "<h3>")
    formatted_text = formatted_text.replace("* ", "• ")

    # 4. 📸 सुपर-फ़िक्स इमेज लॉजिक (अब 100% इमेज आएगी, बिल्ली भी नहीं आएगी)
    city_lower = city.lower()
    if city_lower == "ujjain":
        image_url = "https://loremflickr.com/800/400/ujjain,temple,india/all"
    elif city_lower == "goa":
        image_url = "https://loremflickr.com/800/400/goa,beach,sea/all"
    elif city_lower == "bhopal":
        # भोपाल के लिए एकदम परफेक्ट काम करने वाला और कैट-फ्री लिंक
        image_url = "https://loremflickr.com/800/400/lake,india,boat/all"
    else:
        image_url = f"https://loremflickr.com/800/400/{city_lower},travel,monument/all"

    return render_template('ai_result.html', info=formatted_text, city=city, image_url=image_url, weather="Pleasant")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)