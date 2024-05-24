from flask import Flask, render_template, request, session, redirect, jsonify
import os
from os.path import join
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import sqlite3
from sqlite3 import Error
import hashlib
import pytz


app = Flask(__name__)
app.secret_key = b'fgreji5U((U9((zhrf))))fgdgtz!%4554'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("pythonsqlite.db")
        print("SQLite verzió:", sqlite3.sqlite_version)
    except Error as e:
        print(e)
    return conn

def create_table():
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            sql_query_users = '''CREATE TABLE IF NOT EXISTS users (
                                id integer PRIMARY KEY,
                                username text NOT NULL,
                                password text NOT NULL,
                                timezone text
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
        finally:
            conn.close()

create_table()

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        try:
            conn = create_connection()
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
                return render_template('index.html' , message="Login unsuccessful. Please try again!")
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
            conn = create_connection()
            c = conn.cursor()
            username = request.form['username']
            password = request.form['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            try:
                insert_query = "INSERT INTO users (username, password) VALUES (?, ?)"
                c.execute(insert_query, (username, hashed_password,))
                conn.commit()
                return render_template('sign_up.html', message=f"Hooray! You have successfully registered as {username}.")
            except sqlite3.IntegrityError:
                return render_template('sign_up.html', message2=f"This username is already taken. Please choose another one.")
        except sqlite3.Error as e:
            print("Adatbázis hiba: " + str(e))
        finally:
            if conn:
                conn.close()
    return render_template('sign_up.html')

@app.route('/setmood', methods=['GET','POST'])
def set_mood():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        try:
            user_id = session['user_id']
            mood = request.form['mood']
            conn = create_connection()
            c = conn.cursor()
            c.execute('''SELECT timezone FROM users WHERE id = ?''', (user_id,))
            user_timezone = c.fetchone()[0] or 'UTC'
            user_tz = pytz.timezone(user_timezone)
            current_time = datetime.now(user_tz).strftime('%Y-%m-%d %H:%M')
            c.execute('''SELECT id FROM moods WHERE date = ? AND user_id = ?''', (current_time, user_id))
            row = c.fetchone()

            if row:
                sql_update = '''UPDATE moods SET mood = ? WHERE id = ?'''
                c.execute(sql_update, (mood, row[0]))
            else:
                sql_insert = '''INSERT INTO moods (date, mood, user_id) VALUES (? , ? , ? )'''
                c.execute(sql_insert, (current_time, mood, user_id, ))
                conn.commit()
        except sqlite3.Error as e:
            print("Adatbázis hiba: " + str(e))
        finally:
            if conn:
                conn.close()
    return render_template('logged_in.html')

@app.route('/statistics', methods=['GET', 'POST'])
def generate_chart():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        try:
            start_date = request.form['start_date'] + ' 00:00'
            end_date = request.form['end_date'] + ' 23:59'
            user_id = session['user_id']
            conn = create_connection()
            c = conn.cursor()
            query = "SELECT date, mood FROM moods WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date"
            c.execute(query, (user_id, start_date, end_date))
            data = c.fetchall()
            print(data)

            #diagram generálása
            dates = [datetime.strptime(i[0], '%Y-%m-%d %H:%M') for i in data]
            mood_values = [i[1] for i in data]
            plt.figure(figsize=(10, 6))
            plt.plot(dates, mood_values, marker='o', linestyle='-')
            plt.yticks(range(int(min(mood_values)), int(max(mood_values)) + 1))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gcf().autofmt_xdate()
            plt.xlabel('Date')
            plt.ylabel('Mood level')
            plt.title('Mood chart')
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

@app.route('/set_timezone', methods=['POST'])
def set_timezone():
    if 'user_id' not in session:
        return redirect('/')
    user_id = session['user_id']
    data = request.get_json()
    user_timezone = data['timezone']
    try:
        conn = create_connection()
        c = conn.cursor()
        c.execute('UPDATE users SET timezone = ? WHERE id = ?', (user_timezone, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print("Adatbázis hiba: " + str(e))
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()
    return jsonify({"status": "success"})

#ez mi?
'''if __name__ == "__main__":
    app.run(debug=True, threaded=False)'''

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)