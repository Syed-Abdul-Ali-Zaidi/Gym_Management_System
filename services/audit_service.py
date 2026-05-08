from db.connection import get_db_connection

def get_all_audit():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM audit_view
            ORDER BY timestamp DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error fetching audit_logs: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def search_audit(searchterm):
    '''This will search audit_log(s) by thier USER_ID or USERNAME or ACTION or TABLE_NAME '''
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM audit_view
            WHERE user_id=%s OR username LIKE %s OR action LIKE %s OR table_name LIKE %s
            ORDER BY timestamp DESC
        """

        name_term = f'%{searchterm}%'

        if str(searchterm).isdigit():
            id_val = searchterm
        else:
            id_val = 0
        
        cursor.execute(query,(id_val,name_term, name_term, name_term))
        rows = cursor.fetchall() 
        return rows
    except Exception as e:
        print(f"Error fetching audit_logs: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

def get_by_date_audit(start_date, end_date):
    '''This will filter audit_log(s) by start and enddate'''
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM audit_view
            WHERE DATE(timestamp) BETWEEN %s AND %s
            ORDER BY timestamp DESC
        """
        
        cursor.execute(query,(start_date, end_date))
        rows = cursor.fetchall()  
        return rows
    except Exception as e:
        print(f"Error fetching audit_logs: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()
