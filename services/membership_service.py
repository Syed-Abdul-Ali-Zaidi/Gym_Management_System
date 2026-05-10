from db.connection import get_db_connection
from services.auth_service import set_session_var

def get_all_membership():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT *
            FROM memberships_view
            ORDER by status
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows  # list of dicts, trainer_name will be None if no trainer
    except Exception as e:
        print(f"Error fetching memberships: {e}")
        return []
    finally:
        conn.close()


def search_membership(searchterm, active_filters):
    '''Search membership(s) by member_id or member name or plan_id or trainer_id'''
    conn = get_db_connection()
    try:
        if not active_filters:
            return []

        placeholders = ", ".join(["%s"] * len(active_filters))

        cursor = conn.cursor(dictionary=True)
        query = f"""
            SELECT *
            FROM memberships_view
            WHERE  status IN ({placeholders})  AND (member_id = %s OR member_name LIKE %s OR plan_id = %s OR trainer_id = %s)
            ORDER by status
        """
        # Prepare the NAME term (e.g., "Ali" finds "Ali Ahmed")
        name_term = f'%{searchterm}%'

        id_val = searchterm if str(searchterm).isdigit() else 0

        cursor.execute(query, tuple(active_filters) + (id_val, name_term, id_val, id_val))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error searching memberships: {e}")
        return []
    finally:
        conn.close()

def get_membership_form_data():
    """Fetches clean, active data for the membership enrollment form.""" 
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Members: Exclude banned members, but keep 'Inactive' (expired) for renewals
        # Adjust 'Banned' to whatever your 'forbidden' status is named
        cursor.execute("""
            SELECT member_id, name 
            FROM member 
            WHERE status = "Active"
            ORDER BY name ASC
        """)
        members = cursor.fetchall()
        
        # 2. Plans: Only show plans currently available for sale
        cursor.execute("""
            SELECT plan_id, plan_name, duration_days, fee 
            FROM membership_plan 
            WHERE status = 'Active'
        """)
        plans = cursor.fetchall()
        
        # 3. Trainers: Only show staff currently available for assignment
        cursor.execute("""
            SELECT trainer_id, name, default_fee 
            FROM trainer 
            WHERE status = 'Active'
        """)
        trainers = cursor.fetchall()
        
        return members, plans, trainers
        
    except Exception as e:
        # In a real app, log this to a file
        print(f"Database error during form population: {e}")
        return [], [], []
    finally:
        # Connection always closes even if an error occurs
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

# services/membership_service.py
def sync_statuses_membership():
    """Updates statuses based on the calendar without user intervention."""
    # 1. Upcoming -> Active (Today is the start day)
    # 2. Active -> Expired (Today is past the end day)
    # 3. Upcoming -> Upcoming (Start day is in future)
    # 3. Exclude 'Cancelled' memberships from these updates
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            UPDATE membership ms
            JOIN membership_plan mp ON ms.plan_id = mp.plan_id
            SET ms.status = CASE 
                WHEN DATE_ADD(ms.start_date, INTERVAL mp.duration_days DAY) < CURRENT_DATE 
                    THEN 'Expired'
                    
                WHEN ms.start_date <= CURRENT_DATE 
                    AND DATE_ADD(ms.start_date, INTERVAL mp.duration_days DAY) >= CURRENT_DATE 
                    THEN 'Active'
                    
                WHEN ms.start_date > CURRENT_DATE 
                    THEN 'Upcoming'
                    
                ELSE ms.status
            END
            WHERE ms.status <> 'Cancelled'
         """
        cursor.execute(query)
        
        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error syncing memberships: {e}")
        return False
    finally:
        conn.close()
    # Execute query...

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