import sqlite3

# connect to the db previously generated
connection = sqlite3.connect('events.db')
connection.row_factory = sqlite3.Row

# Below the implementation of the following queries as SQLite commands
# Query 1: List all merchants under a given organization cf6cc433-336c-4d01-947d-21131988fe58, including nested sub-organizations.
# Query 2: Find the total transaction amount per organization.
# Query 3: Detect merchants that have had no transactions.
# Query 4: Find devices that have received scheduled update. 

# Q1
def get_merchants_by_org(organization: str, conn: sqlite3.Connection) -> tuple[sqlite3.Row]:

    cur = conn.cursor()
    try:
        query = f"""
            SELECT mer.*
            FROM organizations org
            JOIN merchants mer
                ON org.organization_id = mer.organization_id
            WHERE org.organization_id = '{organization}' OR org.parent_id = '{organization}'
        """
        
        cur.execute(query)
        return cur.fetchall()
    except sqlite3.Error as e:
        return ("SQLite Error:", e)

# Q2
def get_total_transact_value_per_org(conn: sqlite3.Connection) -> tuple[sqlite3.Row]:

    cur = conn.cursor()
    try:
        query = f"""
            SELECT org.organization_id, sum(transaction_value) as total_transactions_value
            FROM organizations org
            LEFT JOIN merchants merch
                ON org.organization_id = merch.organization_id
            LEFT JOIN transactions trans
                ON merch.merchant_name = trans.merchant_name
            GROUP BY org.organization_id
        """
        cur.execute(query)
        return cur.fetchall()
    except sqlite3.Error as e:
        print("SQLite Error:", e)

# Q3
def get_no_transact_merchants(conn: sqlite3.Connection) -> tuple[sqlite3.Row]:

    cur = conn.cursor()
    try:
        query = f"""
            SELECT merch.merchant_id, merch.merchant_name
            FROM merchants merch
            WHERE merch.merchant_name NOT IN (
                SELECT DISTINCT merchant_name FROM transactions) 
        """
        cur.execute(query)
        return cur.fetchall()
    except sqlite3.Error as e:
        print("SQLite Error:", e)

# Q4
def get_scheduled_update_devices(conn: sqlite3.Connection) -> tuple[sqlite3.Row]:

    cur = conn.cursor()
    try:
        query = f"""
            SELECT dev.device_id, dev.device_name
            FROM devices dev
            WHERE dev.device_id IN (
                SELECT DISTINCT device_id FROM device_updates WHERE status = 'PENDING')
        """
        cur.execute(query)
        return cur.fetchall()
    except sqlite3.Error as e:
        print("SQLite Error:", e)

# query execution

#Q1
print("QUERY1 OUTPUT:\n")
for row in get_merchants_by_org('cf6cc433-336c-4d01-947d-21131988fe58', connection):
    print(dict(row), '\n')

#Q2
print("QUERY2 OUTPUT:\n")
for row in get_total_transact_value_per_org(connection):
    print(dict(row), '\n')

#Q3
print("QUERY3 OUTPUT:\n")
for row in get_no_transact_merchants(connection):
    print(dict(row), '\n')

#Q4
print("QUERY4 OUTPUT:\n")
for row in get_scheduled_update_devices(connection):
    print(dict(row), '\n')