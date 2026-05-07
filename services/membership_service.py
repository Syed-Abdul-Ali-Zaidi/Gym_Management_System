from db.connection import get_db_connection
from services.auth_service import set_session_var

def get_all_membership():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT *
            FROM memberships_view
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows  # list of dicts, trainer_name will be None if no trainer
    except Exception as e:
        print(f"Error fetching memberships: {e}")
        return []
    finally:
        conn.close()


def search_membership(searchterm):
    '''Search membership(s) by member_id or member name'''
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT *
            FROM memberships_view
            WHERE member_id = %s OR member_name LIKE %s
        """
        # Prepare the NAME term (e.g., "Ali" finds "Ali Ahmed")
        name_term = f'%{searchterm}%'

        id_val = searchterm if str(searchterm).isdigit() else 0

        cursor.execute(query, (id_val, name_term))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error searching memberships: {e}")
        return []
    finally:
        conn.close()


def insert_membership(member_id, plan_id, start_date, status, agreed_plan_fee, trainer_id, agreed_trainer_fee):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            INSERT INTO membership 
                (member_id, plan_id, start_date, status, agreed_plan_fee, trainer_id, agreed_trainer_fee)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (member_id, plan_id, start_date, status, agreed_plan_fee, trainer_id, agreed_trainer_fee))
        
        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


def update_membership(member_id, plan_id, start_date, status, agreed_plan_fee, trainer_id, agreed_trainer_fee):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            UPDATE membership
            SET status=%s, agreed_plan_fee=%s, trainer_id=%s, agreed_trainer_fee=%s
            WHERE member_id=%s AND plan_id=%s AND start_date=%s
        """
        cursor.execute(query, (status, agreed_plan_fee, trainer_id, agreed_trainer_fee, member_id, plan_id, start_date))
        
        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


def delete_membership(member_id: int, plan_id: int, start_date):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            DELETE FROM membership
            WHERE member_id=%s AND plan_id=%s AND start_date=%s
        """
        cursor.execute(query, (member_id, plan_id, start_date))
        
        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return False
    finally:
        conn.close()