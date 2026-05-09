from db.connection import get_db_connection
from services.auth_service import set_session_var

def get_all_member():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM member
            ORDER BY status
        """
        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error fetching members: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def search_member(searchterm, active_filters):
    '''This will search member(s) by thier NAME or ID'''
    conn = get_db_connection()
    try:
        if not active_filters:
            return []

        placeholders = ", ".join(["%s"] * len(active_filters))
        
        cursor = conn.cursor(dictionary=True)
        query = f"""
            SELECT * FROM member
            WHERE status IN ({placeholders})  AND (member_id=%s OR name LIKE %s)
            ORDER BY status
        """

        # Prepare the NAME term (e.g., "Ali" finds "Ali Ahmed")
        name_term = f'%{searchterm}%'

        # To prevent the "int vs string" warning, we can safely pass the term
        # or use 0 if it's not a digit for the ID column
        if str(searchterm).isdigit():
            id_val = searchterm
        else:
            id_val = 0
        
        cursor.execute(query,tuple(active_filters) + (id_val, name_term))
        rows = cursor.fetchall() 
        return rows
    except Exception as e:
        print(f"Error fetching members: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def insert_member(name, phone_no, gender, status, join_date):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            INSERT INTO member (name, phone_no, gender, status, join_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, phone_no, gender, status, join_date))
        
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

def update_member(member_id, name, phone_no, gender, status):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            UPDATE member 
            SET name=%s,phone_no=%s,gender=%s,status=%s
            WHERE member_id=%s
        """
        cursor.execute(query, (name, phone_no, gender, status, member_id))

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