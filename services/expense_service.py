from db.connection import get_db_connection
from services.auth_service import set_session_var


def get_all_expense():
    """Returns all expenses joined with their subtype details.
    (e.expense_id, e.amount, e.expense_date, type(Operational OR Salary), oe.category, t.trainer_id, t.trainer_name)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                e.expense_id,
                e.amount,
                e.expense_date,
                CASE 
                    WHEN oe.expense_id IS NOT NULL THEN 'Operational'
                    WHEN se.expense_id IS NOT NULL THEN 'Salary'
                END AS type,
                oe.category,
                t.trainer_id,
                t.name AS trainer_name
            FROM expense e
            LEFT JOIN operational_expense oe ON e.expense_id = oe.expense_id
            LEFT JOIN salary_expense se      ON e.expense_id = se.expense_id
            LEFT JOIN trainer t              ON se.trainer_id = t.trainer_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching expenses: {e}")
        return []
    finally:
        conn.close()

def search_expense(searchterm):
    """Search expense(s) by EXPENSE_ID, CATEGORY (Operational), or TRAINER_NAME (Salary)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                e.expense_id,
                e.amount,
                e.expense_date,
                CASE 
                    WHEN oe.expense_id IS NOT NULL THEN 'Operational'
                    WHEN se.expense_id IS NOT NULL THEN 'Salary'
                END AS type,
                oe.category,
                t.trainer_id,
                t.name AS trainer_name
            FROM expense e
            LEFT JOIN operational_expense oe ON e.expense_id = oe.expense_id
            LEFT JOIN salary_expense se      ON e.expense_id = se.expense_id
            LEFT JOIN trainer t              ON se.trainer_id = t.trainer_id
            WHERE e.expense_id = %s
               OR oe.category LIKE %s
               OR t.name LIKE %s
        """
        name_term = f'%{searchterm}%'
        id_val = searchterm if str(searchterm).isdigit() else 0

        cursor.execute(query, (id_val, name_term, name_term))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error searching expenses: {e}")
        return []
    finally:
        conn.close()

def insert_operational(amount, expense_date, category):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()

        # First insert into EXPENSE table
        query = """
            INSERT INTO expense (amount, expense_date)
            VALUES (%s, %s)
        """
        cursor.execute(query, (amount, expense_date))

        expense_id = cursor.lastrowid  # get the ID of the recently inserted row

        # Now insert into OPERATIONAL_EXPENSE table
        query = """
            INSERT INTO operational_expense (expense_id, category)
            VALUES (%s, %s)
        """
        if category not in ['Utility Bills', 'Rent', 'Marketing&Sales', 'Maintenance&Supplies', 'Extras']:
            category = 'Extras'

        cursor.execute(query, (expense_id, category))

        
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

def insert_salary(amount, expense_date, trainer_id):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()

        # First insert into EXPENSE table
        query = """
            INSERT INTO expense (amount, expense_date)
            VALUES (%s, %s)
        """
        cursor.execute(query, (amount, expense_date))

        expense_id = cursor.lastrowid  # get the ID of the recently inserted row

        # Now insert into SALARY_EXPENSE table
        query = """
            INSERT INTO salary_expense (expense_id, trainer_id)
            VALUES (%s, %s)
        """
        cursor.execute(query, (expense_id, trainer_id))

        
        # If everything is perfect, save it
        conn.commit()
        return True
    except Exception as e:
        # If ANY error happens, undo everything
        conn.rollback() 
        print(f"Error: {e}")
        return False
    finally:
        # Always close the pipe
        conn.close()

def update(expense_id, amount, expense_date):
    """Only base expense fields (amount, expense_date) are editable."""
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()
        query = """
            UPDATE expense
            SET amount=%s, expense_date=%s
            WHERE expense_id=%s
        """
        cursor.execute(query, (amount, expense_date, expense_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def delete(expense_id: int):
    conn = get_db_connection()
    try:
        set_session_var(conn)
        cursor = conn.cursor()

        # Step 1 — delete from OPERATIONAL_EXPENSE first
        query = """
            DELETE FROM operational_expense
            WHERE expense_id=%s
        """
        cursor.execute(query, (expense_id,))

        # Step 2 — delete from SALARY_EXPENSE second
        query = """
            DELETE FROM salary_expense
            WHERE expense_id=%s
        """
        cursor.execute(query, (expense_id,))

        # Step 3 — delete from EXPENSE last (parent table)
        query = """
            DELETE FROM expense
            WHERE expense_id=%s
        """
        cursor.execute(query, (expense_id,))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return False
    finally:
        conn.close()