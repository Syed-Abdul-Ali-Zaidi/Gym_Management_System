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


def search_audit(searchterm, active_filters, start_date=None, end_date=None):
    '''Combines Action, Date, and Search term filtering into one query'''
    conn = get_db_connection()
    try:
        if not active_filters:
            return []

        cursor = conn.cursor(dictionary=True)
        params = []

        # The mandatory Action filter
        placeholders = ", ".join(["%s"] * len(active_filters))
        query = f"""SELECT * FROM audit_view
                  WHERE action IN ({placeholders})"""
        params.extend(active_filters)

        # Date Filter, if there is date then add it
        if start_date and end_date:
            query += " AND DATE(timestamp) BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        # 3. Search Logic, if there is search term then add it
        name_term = f'%{searchterm}%'

        if searchterm:
            name_term = f'%{searchterm.strip()}%'
            if str(searchterm).isdigit():
                id_val = searchterm
            else:
                id_val = 0
            
            query += " AND (user_id = %s OR username LIKE %s OR table_name LIKE %s)"
            params.extend([id_val, name_term, name_term])

        # 4. Final Ordering
        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        return cursor.fetchall()

    except Exception as e:
        print(f"Error fetching combined audit logs: {e}")
        return []
    finally:
        conn.close()