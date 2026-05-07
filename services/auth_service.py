from db.connection import get_db_connection

current_session = {"user_id": None, "username": None, "role": None}

def login(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM user
            WHERE username=%s AND password=%s
        """
        cursor.execute(query,(username,password))
        row = cursor.fetchone() 
        
        if row:
            current_session["user_id"] = row["user_id"]
            current_session["username"] = row["username"]
            current_session["role"] = row["role"]
    
        return row # returns dictionary
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None    # Return None so the UI doesn't crash
    finally:
        conn.close()
    
def get_session():
    return current_session

def is_admin():
    return current_session.get("role") == "Admin"
    

def set_session_var(conn):
    """Must be called before every DML so audit triggers have @current_user_id."""
    cursor = conn.cursor()
    cursor.execute("SET @current_user_id = %s", (current_session["user_id"],))
    cursor.close()