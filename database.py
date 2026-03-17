import sqlite3

def create_db():
    """Create database tables for CareerAI"""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Users table with profile information
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        job_title TEXT DEFAULT '',
        education TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Migration: Add missing columns if they don't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN job_title TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        c.execute("ALTER TABLE users ADD COLUMN education TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        c.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Resumes table
    c.execute("""
    CREATE TABLE IF NOT EXISTS resumes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        file_path TEXT,
        score INTEGER,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_email) REFERENCES users(email)
    )
    """)

    try:
        c.execute("ALTER TABLE resumes ADD COLUMN uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Skills table to store detected skills
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_skills(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        resume_id INTEGER,
        skill TEXT,
        FOREIGN KEY (user_email) REFERENCES users(email),
        FOREIGN KEY (resume_id) REFERENCES resumes(id)
    )
    """)

    # Career path table
    c.execute("""
    CREATE TABLE IF NOT EXISTS career_path(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        current_level TEXT,
        target_level TEXT,
        timeline TEXT,
        FOREIGN KEY (user_email) REFERENCES users(email)
    )
    """)

    conn.commit()
    conn.close()

create_db()