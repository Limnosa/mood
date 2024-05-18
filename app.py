from flask import Flask, render_template, request, session
import os
from os.path import join
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import sqlite3
import hashlib


app = Flask(__name__)
app.secret_key = b'fgreji5U((U9((zhrf))))fgdgtz!%4554'

conn = sqlite3.connect("pythonsqlite.db")
c = conn.cursor()

# Kapcsolat ellenőrzése
if conn is not None:
    print("Az adatbáziskapcsolat létrejött.")
else:
    print("Az adatbáziskapcsolat nem jött létre.")

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("pythonsqlite.db")
        print("SQLite verzió:", sqlite3.sqlite_version)
    except Error as e:
        print(e)
    return conn

def create_table():
    try:
        c = conn.cursor()
        sql_query_users = '''CREATE TABLE IF NOT EXISTS users (
                            id integer PRIMARY KEY,
                            username text NOT NULL,
                            password text NOT NULL 
                        );'''
        sql_query_moods = '''CREATE TABLE IF NOT EXISTS moods (
                            id integer PRIMARY KEY,
                            date text,
                            mood integer,
                            user_id integer,
                            FOREIGN KEY (user_id) REFERENCES users (id) 
                        );'''
        c.execute(sql_query_users)
        c.execute(sql_query_moods)
        conn.commit()
    except Error as e:
        print(e)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        try:
            conn = sqlite3.connect("pythonsqlite.db")
            c = conn.cursor()
            username = request.form['username']
            password = request.form['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            sql_query = "SELECT * FROM users WHERE username = ? AND password = ? "
            c.execute(sql_query, (username, hashed_password))
            results = c.fetchall()
            if results:
                session['user_id'] = results[0][0]
                return render_template("logged_in.html")
            else:
                return render_template('index.html' , message="Sikertelen bejelentkezés. Próbáld újra!")
        except sqlite3.Error as e:
            print("Adatbázis hiba: " + str(e))
        finally:
            if conn:
                conn.close()

    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        try:
            conn = sqlite3.connect("pythonsqlite.db")
            c = conn.cursor()
            username = request.form['username']
            password = request.form['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            try:
                insert_query = "INSERT INTO users (username, password) VALUES (?, ?)"
                c.execute(insert_query, (username, hashed_password,))
                conn.commit()
                return render_template('sign_up.html', message=f"Gratulálunk! Sikeresen regisztráltál {username} néven!")
            except sqlite3.IntegrityError:
                return render_template('sign_up.html', message2=f"{username} már szerepel az adatbázisban. Válassz másik felhasználónevet!")
        except sqlite3.Error as e:
            print("Adatbázis hiba: " + str(e))
        finally:
            if conn:
                conn.close()
    return render_template('sign_up.html')

@app.route('/setmood', methods=['GET','POST'])
def set_mood():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        try:
            user_id = session['user_id']
            mood = request.form['mood']
            conn = sqlite3.connect("pythonsqlite.db")
            c = conn.cursor()
            sql_query = '''INSERT INTO moods (date, mood, user_id) VALUES (CURRENT_TIMESTAMP , ? , ? )'''
            c.execute(sql_query, (mood, user_id, ))
        except sqlite3.Error as e:
            print("Adatbázis hiba: " + str(e))
        finally:
            if conn:
                conn.commit()
                conn.close()
    return render_template('logged_in.html')

@app.route('/statistics', methods=['GET', 'POST'])
def generate_chart():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        try:
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            user_id = session['user_id']
            conn = sqlite3.connect('pythonsqlite.db')
            c = conn.cursor()
            query = "SELECT date, mood FROM moods WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date"
            c.execute(query, (user_id, start_date, end_date))
            data = c.fetchall()
            print(data)
            #conn.close()

            #diagram generálása
            dates = [i[0] for i in data]
            mood_values = [i[1] for i in data]
            dates = [datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') for date_str in dates]
            plt.figure(figsize=(10, 6))
            plt.plot(dates, mood_values, marker='o', linestyle='-')
            plt.yticks(range(int(min(mood_values)), int(max(mood_values)) + 1))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gcf().autofmt_xdate()
            plt.xlabel('Dátum')
            plt.ylabel('Hangulatszint')
            plt.title('Hangulatszint időben')
            plt.grid(True)

            # Diagram mentése képként
            c.execute("SELECT username FROM users WHERE id=?", (user_id,))
            name = c.fetchone()[0]
            save_directory = 'static/moodpics/'
            filename = f"{name}_{start_date.replace(':', '').replace('-', '_')}_{end_date.replace(':', '').replace('-', '_')}.png"
            save_path = os.path.join(save_directory, filename)
            plt.savefig(save_path, format='png')
            plt.close()
            conn.close()
            return render_template('statistics.html', image_path=save_path)

        except sqlite3.Error as e:
            print("Adatbázis hiba: " + str(e))

    return render_template('statistics.html')

#ez mi?
'''if __name__ == "__main__":
    app.run(debug=True, threaded=False)'''

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)