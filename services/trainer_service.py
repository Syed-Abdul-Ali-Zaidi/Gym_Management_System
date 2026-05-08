from db.connection import get_db_connection
from services.auth_service import set_session_var

def get_all_trainer():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM trainer
            ORDER BY status
        """
        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error fetching trainer: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def search_trainer(searchterm):
    '''This will search trainer(s) by thier NAME or ID'''
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM trainer
            WHERE trainer_id=%s OR name LIKE %s
            ORDER BY status
        """

        name_term = f'%{searchterm}%'
        if str(searchterm).isdigit():
            id_val = searchterm
        else:
            id_val = 0
        
        cursor.execute(query,(id_val,name_term))
        rows = cursor.fetchall() 
        return rows
    except Exception as e:
        print(f"Error fetching trainer: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def insert_trainer(name, phone_no, salary, specialization, status, default_fee):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            INSERT INTO trainer (name, phone_no, salary, specialization, status, default_fee)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, phone_no, salary, specialization, status, default_fee))
        
        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        conn.rollback() 
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def update_trainer(trainer_id, name, phone_no, salary, specialization, status, default_fee):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            UPDATE trainer
            SET name=%s, phone_no=%s, salary=%s, specialization=%s, status=%s, default_fee=%s
            WHERE trainer_id=%s
        """
        cursor.execute(query, (name, phone_no, salary, specialization, status, default_fee, trainer_id))

        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        conn.rollback() 
        print(f"Error: {e}")
        return False
    finally:
        conn.close()
        