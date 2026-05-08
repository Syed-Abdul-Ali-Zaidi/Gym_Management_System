from db.connection import get_db_connection
from services.auth_service import set_session_var

def get_all_user():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM user
        """
        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def search_user(searchterm):
    '''This will search user(s) by thier username or ID'''
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM user
            WHERE user_id=%s OR username LIKE %s
        """

        # Prepare the username term (e.g., "Ali" finds "Ali Ahmed")
        username_term = f'%{searchterm}%'

        if str(searchterm).isdigit():
            id_val = searchterm
        else:
            id_val = 0
        
        cursor.execute(query,(id_val,username_term))
        rows = cursor.fetchall() 
        return rows
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def insert_user(username, password, role, status, date_created):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            INSERT INTO user (username, password, role, status, date_created)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (username, password, role, status, date_created))
        
        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        # If ANY error happens, undo everything
        conn.rollback() 
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def update_user(user_id, username, password, role, status):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            UPDATE user 
            SET username=%s,password=%s,role=%s,status=%s
            WHERE user_id=%s
        """
        cursor.execute(query, (username, password, role, status, user_id))

        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        # If ANY error happens, undo everything
        conn.rollback() 
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

