import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import stripe

app = Flask(__name__)
stripe.api_key = "sk_test_51Nc4h6SCPZp6aY1nodaHLdES0vdpBDPAB1TnILueMqHxzaJaahzeSLhE0EnVKfO4fqXgSwhZAlOEWrTKqZbsMdFH00nqq04GNk"
# SQLite3 database setup
DATABASE = 'users.db'

def create_table():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
            user = cursor.fetchone()
            if user:
                return render_template('plan.html', username=user[1])
            else:
                return "Invalid credentials. Please try again."

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                return "User with this email already exists. Please use a different email."

            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
            conn.commit()
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    price = request.form.get('priceId')
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items = [
                {
                    'price': price,
                    'quantity': 1
                }
            ],
            mode = "subscription",
            success_url = "http://127.0.0.1:5500/templates/success.html",
            cancel_url = "http://127.0.0.1:5500/templates/cancel.html"
        )

    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
