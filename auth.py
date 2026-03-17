import sqlite3

def register_user(name, email, password, job_title="", education=""):
    """
    Register a new user with profile information
    """
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users(name, email, password, job_title, education) VALUES(?, ?, ?, ?, ?)",
            (name, email, password, job_title, education)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False


def login_user(email, password):
    """
    Authenticate user credentials
    """
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    data = c.fetchone()
    conn.close()
    return data


def get_user_profile(email):
    """
    Get user profile information
    """
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    c.execute(
        "SELECT name, email, job_title, education FROM users WHERE email=?",
        (email,)
    )
    
    data = c.fetchone()
    conn.close()
    
    if data:
        return {
            'name': data[0],
            'email': data[1],
            'job_title': data[2],
            'education': data[3]
        }
    return None


def update_user_profile(email, name, job_title, education):
    """
    Update user profile information
    """
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    try:
        c.execute(
            "UPDATE users SET name=?, job_title=?, education=? WHERE email=?",
            (name, job_title, education, email)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False