from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "events.db"

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL
                 )''')
    # create Events table
    c.execute('''CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL
                 )''')
    # Registrations table
    c.execute('''CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    student_name TEXT,
                    UNIQUE(event_id, student_name),
                    FOREIGN KEY(event_id) REFERENCES events(id)
                 )''')
    # Default user
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("abdul", "1234"))
    conn.commit()
    conn.close()

init_db()

# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        return jsonify({"message": "Username and password cannot be empty"}), 400

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Incorrect username or password"}), 401

# ---------- CREATE EVENT ----------
@app.route("/events", methods=["POST"]) #when the client wants to send new data
def create_event():
    data = request.json
    name = data.get("name", "").strip()
    date = data.get("date", "").strip()
    
    if not name:
        return jsonify({"message": "Event name cannot be empty"}), 400

    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO events (name, date) VALUES (?, ?)", (name, date))
    event_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"message": "Event created", "event": {"id": event_id, "name": name, "date": date}}), 201

# ---------- LIST EVENTS ----------
@app.route("/events", methods=["GET"])
def list_events():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, name, date FROM events")
    events = []
    for row in c.fetchall():
        event_id, name, date = row
        c.execute("SELECT COUNT(*) FROM registrations WHERE event_id=?", (event_id,))
        count = c.fetchone()[0]
        events.append({"id": event_id, "name": name, "date": date, "registrations_count": count})
    conn.close()
    return jsonify(events), 200

# ---------- REGISTER STUDENT ----------
@app.route("/events/<int:event_id>/register", methods=["POST"])
def register_student(event_id):
    data = request.json
    student_name = data.get("name", "").strip()
    if not student_name:
        return jsonify({"message": "Student name cannot be empty"}), 400

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE id=?", (event_id,))
    event = c.fetchone()
    if not event:
        conn.close()
        return jsonify({"message": "Event not found"}), 404

    # Check for duplicate registration
    c.execute("SELECT id FROM registrations WHERE event_id=? AND student_name=?", (event_id, student_name))
    if c.fetchone():
        conn.close()
        return jsonify({"message": f"{student_name} is already registered for {event[1]}"}), 400

    c.execute("INSERT INTO registrations (event_id, student_name) VALUES (?, ?)", (event_id, student_name))
    conn.commit()
    conn.close()
    return jsonify({"message": f"{student_name} successfully registered for {event[1]}", "event": {"id": event[0], "name": event[1]}}), 200

# ---------- VIEW REGISTERED STUDENTS ----------
@app.route("/events/<int:event_id>/registrations", methods=["GET"])
def view_registrations(event_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT name FROM events WHERE id=?", (event_id,))
    event = c.fetchone()
    if not event:
        conn.close()
        return jsonify({"message": "Event not found"}), 404
    c.execute("SELECT student_name FROM registrations WHERE event_id=?", (event_id,))
    students = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify({"event_name": event[0], "students": students}), 200

if __name__ == "__main__":
    app.run(debug=True)
