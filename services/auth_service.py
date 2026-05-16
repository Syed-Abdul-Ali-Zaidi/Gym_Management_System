from db.connection import get_db_connection

current_session = {"user_id": None, "username": None, "role": None}

def login(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM user
            WHERE username=%s AND password=%s
        """
        cursor.execute(query,(username,password))
        row = cursor.fetchone() 
        
        if row:
            current_session["user_id"] = row["user_id"]
            current_session["username"] = row["username"]
            current_session["role"] = row["role"]
    
        return row # returns dictionary
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None    # Return None so the UI doesn't crash
    finally:
        conn.close()
    
def get_session():
    return current_session

def is_admin():
    return current_session.get("role") == "Admin"
    

def set_session_var(conn):
    """Must be called before every DML so audit triggers have @current_user_id."""
    cursor = conn.cursor()
    cursor.execute("SET @current_user_id = %s", (current_session["user_id"],))
    cursor.close()

def get_dashboard_data():
    "Will return all the data in a Dict for Dashborad"
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    data = {}
    try:
        # 1. Total Active Members
        cursor.execute("Select COUNT(*) AS total from member WHERE status = 'Active'")
        data['active_members'] = cursor.fetchone()['total']

        # 2. Total Active Memberships
        cursor.execute("SELECT COUNT(*) AS total from membershipS_view WHERE status = 'Active'")
        data['active_memberships'] = cursor.fetchone()['total']

        # 3. Paid Active Memberships
        query = """
            SELECT
                COUNT(p.member_id) AS total
            FROM memberships_view mv
            INNER JOIN payment_view p 
                ON mv.member_id = p.member_id 
                AND mv.plan_id = p.plan_id 
                AND mv.start_date = p.start_date
            WHERE
                mv.status = 'Active' 
                AND p.payment_status = 'Paid'
                """
        cursor.execute(query)
        data['paid_active_memberships'] = cursor.fetchone()['total'] or 0

         # 4. Unpaid Active Memberships
        query = """
            SELECT
                COUNT(p.member_id) AS total
            FROM memberships_view mv
            INNER JOIN payment_view p 
                ON mv.member_id = p.member_id 
                AND mv.plan_id = p.plan_id 
                AND mv.start_date = p.start_date
            WHERE
                mv.status = 'Active' 
                AND p.payment_status = 'Unpaid'
                """
        cursor.execute(query)
        data['unpaid_active_memberships'] = cursor.fetchone()['total'] or 0

        # 5. Current Revenue, Expense & Profit/Loss
        cursor.execute("""
            SELECT SUM(amount) AS total FROM payment_view
            WHERE payment_date >= DATE_FORMAT(NOW(), '%Y-%m-01')
                AND payment_date < DATE_FORMAT(NOW() + INTERVAL 1 MONTH, '%Y-%m-01')
          """)
        data['current_revenue'] = cursor.fetchone()['total'] or 0.0

        cursor.execute("""
            SELECT SUM(amount) AS total FROM expense
            WHERE expense_date >= DATE_FORMAT(NOW(), '%Y-%m-01')
                AND expense_date < DATE_FORMAT(NOW() + INTERVAL 1 MONTH, '%Y-%m-01')
          """)
        data['current_expense'] = cursor.fetchone()['total'] or 0.0
        data['current_pro_loss'] = float(data['current_revenue']) - float(data['current_expense'])

        # 5. Past Revenue, Expense & Profit/Loss
        cursor.execute("""
            SELECT SUM(amount) AS total FROM payment_view
            WHERE payment_date >= DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01')
                AND payment_date < DATE_FORMAT(NOW(), '%Y-%m-01')
          """)
        data['past_revenue'] = cursor.fetchone()['total'] or 0.0

        cursor.execute("""
            SELECT SUM(amount) AS total FROM expense
            WHERE expense_date >= DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01')
                AND expense_date < DATE_FORMAT(NOW(), '%Y-%m-01')
          """)
        data['past_expense'] = cursor.fetchone()['total'] or 0.0
        data['past_pro_loss'] = float(data['past_revenue']) - float(data['past_expense'])


    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        # Fallback defaults if the query fails
        data = {
            'active_members': 0, 'active_memberships': 0, 'paid_active_memberships': 0, 'unpaid_active_memberships': 0,
            'current_revenue': 0.0, 'current_expense': 0.0, 'current_pro_loss': 0.0,
            'past_revenue': 0.0, 'past_expense': 0.0, 'past_pro_loss': 0.0
        }
    finally:
        conn.close()
        
    return data