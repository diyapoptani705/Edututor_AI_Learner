import sqlite3, hashlib, os
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / 'edututor.db'

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            full_name TEXT NOT NULL,
            grade TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS quiz_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL, topic TEXT NOT NULL, difficulty TEXT NOT NULL,
            score INTEGER NOT NULL, total INTEGER NOT NULL,
            taken_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS chat_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, subject TEXT NOT NULL,
            question TEXT NOT NULL, answer TEXT NOT NULL, asked_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS study_plans(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            plan_text TEXT NOT NULL, created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS sessions(
            token TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        ''')

def hash_password(password, salt=None):
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120_000).hex()
    return digest, salt

def create_user(username, password, full_name, grade):
    username = username.strip().lower()
    if len(username) < 3 or len(password) < 6:
        raise ValueError('Username must be 3+ characters and password must be 6+ characters.')
    digest, salt = hash_password(password)
    try:
        with conn() as c:
            cur = c.execute('INSERT INTO users(username,password_hash,salt,full_name,grade,created_at) VALUES(?,?,?,?,?,?)',
                            (username,digest,salt,full_name.strip(),grade,datetime.now().isoformat(timespec='seconds')))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError('Username already exists.')

def authenticate(username, password):
    with conn() as c:
        r = c.execute('SELECT * FROM users WHERE username=?', (username.strip().lower(),)).fetchone()
    if not r: return None
    digest, _ = hash_password(password, r['salt'])
    if digest != r['password_hash']: return None
    return dict(r)

def save_session(token, user_id):
    with conn() as c:
        c.execute('INSERT OR REPLACE INTO sessions(token,user_id,created_at) VALUES(?,?,?)',
                  (token,user_id,datetime.now().isoformat(timespec='seconds')))

def user_for_token(token):
    if not token: return None
    with conn() as c:
        r = c.execute('SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token=?',(token,)).fetchone()
    return dict(r) if r else None

def delete_session(token):
    with conn() as c: c.execute('DELETE FROM sessions WHERE token=?',(token,))

def save_quiz(user_id, subject, topic, difficulty, score, total):
    with conn() as c:
        c.execute('INSERT INTO quiz_results(user_id,subject,topic,difficulty,score,total,taken_at) VALUES(?,?,?,?,?,?,?)',
                  (user_id,subject,topic,difficulty,score,total,datetime.now().isoformat(timespec='seconds')))

def quiz_rows(user_id):
    with conn() as c:
        return [dict(r) for r in c.execute('SELECT * FROM quiz_results WHERE user_id=? ORDER BY taken_at ASC',(user_id,)).fetchall()]

def save_chat(user_id, subject, question, answer):
    with conn() as c: c.execute('INSERT INTO chat_history(user_id,subject,question,answer,asked_at) VALUES(?,?,?,?,?)',
                                  (user_id,subject,question,answer,datetime.now().isoformat(timespec='seconds')))

def chats(user_id, limit=30):
    with conn() as c:
        return [dict(r) for r in c.execute('SELECT * FROM chat_history WHERE user_id=? ORDER BY id DESC LIMIT ?',(user_id,limit)).fetchall()]

def save_plan(user_id, text):
    with conn() as c: c.execute('INSERT INTO study_plans(user_id,plan_text,created_at) VALUES(?,?,?)',
                                 (user_id,text,datetime.now().isoformat(timespec='seconds')))

def latest_plan(user_id):
    with conn() as c:
        r=c.execute('SELECT * FROM study_plans WHERE user_id=? ORDER BY id DESC LIMIT 1',(user_id,)).fetchone()
    return dict(r) if r else None
