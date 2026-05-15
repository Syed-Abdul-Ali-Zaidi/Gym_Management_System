from db.connection import get_db_connection

# ── Report 1: Active Members per Plan ─────────────────────────────────────────
def active_members_per_plan():
    ''' Group by plan_name to see which subscription type is most popular'''
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                mp.plan_id,
                mp.plan_name,
                COUNT(p.member_id) AS active_count,
                COALESCE(SUM(
                    CASE 
                        WHEN p.payment_status = 'Paid' THEN mv.agreed_plan_fee 
                        ELSE 0 
                    END
                ), 0) AS revenue
            FROM membership_plan mp
            LEFT JOIN memberships_view mv 
                ON mp.plan_id = mv.plan_id 
                AND mv.status = 'Active'
            LEFT JOIN payment_view p 
                ON mv.member_id = p.member_id 
                AND mv.plan_id = p.plan_id 
                AND mv.start_date = p.start_date 
                AND p.payment_status = 'Paid'
            GROUP BY mp.plan_id, mp.plan_name
            ORDER BY active_count DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error Generating plan report: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

# ── Report 2: Trainer Workload ────────────────────────────────────────────────
def trainer_workload():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                t.trainer_id, 
                t.name, 
                t.salary,
                COUNT(p.member_id) AS assigned_members,
                COALESCE(SUM(
                    CASE 
                        WHEN p.payment_status = 'Paid' THEN mv.agreed_trainer_fee 
                        ELSE 0 
                    END
                ), 0) AS trainer_revenue
            FROM trainer t
            LEFT JOIN memberships_view mv 
                ON t.trainer_id = mv.trainer_id 
                AND mv.status = 'Active'
            LEFT JOIN payment_view p 
            ON mv.member_id = p.member_id 
            AND mv.plan_id = p.plan_id 
            AND mv.start_date = p.start_date 
            AND p.payment_status = 'Paid'
            WHERE t.status = 'Active'
            GROUP BY t.trainer_id, t.name, t.salary
            ORDER BY assigned_members DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error Generating trainer workload report: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

# ── Report 3: Monthly Revenue ─────────────────────────────────────────────────
def monthly_revenue():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                YEAR(payment_date)  AS year,
                MONTH(payment_date) AS month,
                SUM(amount)         AS total_revenue,
                COUNT(*)            AS no_of_transaction
            FROM payment_view
            WHERE payment_status = 'Paid'
            GROUP BY year, month
            ORDER BY year DESC, month DESC
    """
        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error Generating Revenue report: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

# ── Report 4: Monthly Expenses ────────────────────────────────────────────────
def monthly_expenses():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                YEAR(expense_date)  AS year,
                MONTH(expense_date) AS month,
                SUM(amount)         AS total_expense,
                COUNT(*)            AS no_of_transaction
            FROM expense
            GROUP BY year, month
            ORDER BY year DESC, month DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall() 
        
        return rows # returns list of dictionaries where each dictionary is a row
    except Exception as e:
        print(f"Error Generating Expense report: {e}")
        return []    # Return an empty list so the UI doesn't crash
    finally:
        conn.close()

# ── Report 5: Monthly Profit ────────────────────────────────────────────────
def monthly_profit():
    '''Returns a Full Outer Join of Revenue and Expenses to show true Net Profit'''
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # We combine LEFT and RIGHT joins to simulate a FULL JOIN
        query = """
            SELECT
                COALESCE(r.year, e.year)   AS year,
                COALESCE(r.month, e.month) AS month,
                COALESCE(r.total_revenue, 0)  AS revenue,
                COALESCE(e.total_expenses, 0) AS expenses,
                COALESCE(r.total_revenue, 0) - COALESCE(e.total_expenses, 0) AS profit
            FROM
                (SELECT YEAR(payment_date) AS year,
                        MONTH(payment_date) AS month,
                        SUM(amount) AS total_revenue
                FROM payment_view
                WHERE payment_status = 'Paid'
                GROUP BY year, month) r
            LEFT JOIN
                (SELECT YEAR(expense_date) AS year,
                        MONTH(expense_date) AS month,
                        SUM(amount) AS total_expenses
                FROM expense
                GROUP BY year, month) e
            ON r.year = e.year AND r.month = e.month

            UNION

            SELECT
                COALESCE(r.year, e.year),
                COALESCE(r.month, e.month),
                COALESCE(r.total_revenue, 0),
                COALESCE(e.total_expenses, 0),
                COALESCE(r.total_revenue, 0) - COALESCE(e.total_expenses, 0) AS profit
            FROM
                (SELECT YEAR(payment_date) AS year,
                        MONTH(payment_date) AS month,
                        SUM(amount) AS total_revenue
                FROM payment_view
                WHERE payment_status = 'Paid'
                GROUP BY year, month) r
            RIGHT JOIN
                (SELECT YEAR(expense_date) AS year, MONTH(expense_date) AS month,
                        SUM(amount) AS total_expenses
                 FROM expense GROUP BY year, month) e
            ON r.year = e.year AND r.month = e.month

            ORDER BY year DESC, month DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as error:
        print(f"Profit Report Error: {error}")
        return []
    finally:
        conn.close()
 