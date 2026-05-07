from db.connection import get_db_connection
from services.auth_service import set_session_var

def get_all_payment():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM payment_view
            ORDER BY payment_status DESC, payment_date DESC
        """

        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error fetching paymnets: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def search_payment(searchterm):
    '''This will search payment(s) by thier MEMBER_ID or PLAN_ID with FULL details'''
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM payment_view
            WHERE member_id=%s OR plan_id=%s
        """

        # To prevent the "int vs string" warning, we can safely pass the term
        # or use 0 if it's not a digit for the ID column
        if str(searchterm).isdigit():
            id_val = searchterm
        else:
            id_val = 0

        cursor.execute(query,(id_val,id_val))
        rows = cursor.fetchall() 
        return rows
    except Exception as e:
        print(f"Error fetching payments: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def insert_payment(member_id, plan_id, start_date, payment_date, method):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            INSERT INTO payment (member_id, plan_id, start_date, payment_date, method)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (member_id, plan_id, start_date, payment_date, method))
        
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


def delete_payment(member_id, plan_id, start_date):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            DELETE FROM payment
            WHERE member_id=%s AND plan_id=%s AND start_date=%s
        """

        cursor.execute(query,(member_id, plan_id, start_date))

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