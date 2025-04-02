from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import sqlite3
from dotenv import load_dotenv 
import openai  
import os

load_dotenv()  
openai.api_key = os.getenv("OPENAI_API_KEY")  

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


# Database setup
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS symptoms (
                    id INTEGER PRIMARY KEY,
                    user TEXT,
                    symptoms TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/')
def index():
    return render_template("index.html")

@app.route('/symptom-checker', methods=['GET', 'POST'])
@login_required
def symptom_checker():
    if request.method == 'POST':
        data = request.get_json()
        symptoms_text = data.get("symptoms", "")
        if not symptoms_text:
            return jsonify({"error": "Please provide symptoms."}), 400
        
        try:
            prompt = f"Based on the following symptoms, provide a possible medical condition and the probability that is the diagnosis (as a percentage): {symptoms_text}"
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical symptom analyzer. Provide responses in the format 'Condition: [condition name], Confidence: [percentage]'. Only suggest common and well-known conditions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            
            result = response.choices[0].message.content
            
      
            try:
                parts = result.split(',')
                condition = parts[0].split(':')[1].strip()
                confidence = float(parts[1].split(':')[1].strip().replace('%', '')) / 100
            except:
                condition = result
                confidence = 0.5  
            
            if 'user' in session:
                conn = sqlite3.connect("database.db")
                c = conn.cursor()
                c.execute("INSERT INTO symptoms (user, symptoms) VALUES (?, ?)", 
                         (session['user'], symptoms_text))
                conn.commit()
                conn.close()
            
            return jsonify({
                "predictions": {
                    "condition": condition,
                    "confidence": confidence
                }
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
    return render_template("checker.html")


@app.route('/history')
@login_required
def history():
    if 'user' in session:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT symptoms FROM symptoms WHERE user = ?", (session['user'],))
        history_data = c.fetchall()
        conn.close()
        return render_template("history.html", history=history_data)
    return render_template("history.html")

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        query = request.form.get("query")
        prompt = f"Provide recommendations and educational content on {query}."
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You provide healthcare recommendations and education."},
                    {"role": "user", "content": prompt},
                    
                ],
                max_tokens = 500

            )
            # Extract the text from the API response
            result = response.choices[0].message.content
            return render_template("search.html", query=query, result=result)
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    
    return render_template("search.html", query=None, result=None)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('signin'))  
        except sqlite3.IntegrityError:
            return "Username or email already exists. Please try again.", 400

    return render_template('signup.html')  

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username  
            return redirect(url_for('index'))  
        else:
            return "Invalid username or password. Please try again.", 401

    return render_template('signin.html')  

if __name__ == '__main__':
    app.run(debug=True)