from db.connection import get_db_connection
from services.auth_service import set_session_var

def get_all_plan():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM membership_plan
        """
        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error fetching plans: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def search_plan(searchterm):
    '''This will search plan(s) by thier NAME or ID'''
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM membership_plan
            WHERE plan_id=%s OR plan_name LIKE %s
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
        print(f"Error fetching plans: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def insert_plan(plan_name, duration_days, fee):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            INSERT INTO membership_plan (plan_name, duration_days, fee)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (plan_name, duration_days, fee))
        
        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        conn.rollback() 
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def update_plan(plan_id, plan_name, duration_days, fee):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            UPDATE membership_plan
            SET plan_name=%s, duration_days=%s, fee=%s
            WHERE plan_id=%s
        """
        cursor.execute(query, (plan_name, duration_days, fee, plan_id))

        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        conn.rollback() 
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def delete_plan(plan_id: int):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            DELETE FROM membership_plan
            WHERE plan_id=%s
        """

        cursor.execute(query,(plan_id,))

        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        conn.rollback() 
        print(f"Error: {e}")
        return False
    finally:
        conn.close()