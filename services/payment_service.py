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

def search_payment(searchterm, status_active_filters, method_active_filters):
    '''This will search payment(s) by thier MEMBER_ID or Member_Name or PLAN_ID with Filtes of Status and Method'''
    conn = get_db_connection()
    try:
        if not status_active_filters:
            return []

        status_placeholders = ", ".join(["%s"] * len(status_active_filters))
        method_placeholders = ", ".join(["%s"] * len(method_active_filters))

        # Prepare the NAME term (e.g., "Ali" finds "Ali Ahmed")
        name_term = f'%{searchterm}%'

        if str(searchterm).isdigit():
            id_val = searchterm
        else:
            id_val = 0

        cursor = conn.cursor(dictionary=True)
        if method_active_filters:
            query = f"""
                SELECT *
                FROM payment_view
                WHERE  payment_status IN ({status_placeholders}) AND (method IN ({method_placeholders}) OR method IS NULL) AND (member_id = %s OR member_name LIKE %s OR plan_id = %s)
                ORDER by payment_status
            """
            cursor.execute(query, tuple(status_active_filters) + tuple(method_active_filters) + (id_val, name_term, id_val))
        else:
            query = f"""
                SELECT *
                FROM payment_view
                WHERE  payment_status IN ({status_placeholders}) AND (member_id = %s OR member_name LIKE %s OR plan_id = %s)
                ORDER by payment_status
            """
            cursor.execute(query, tuple(status_active_filters) + (id_val, name_term, id_val))

        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error searching memberships: {e}")
        return []
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