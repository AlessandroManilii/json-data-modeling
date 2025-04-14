import sqlite3

# to be executed once
def create_tables(conn: sqlite3.Connection):
    cur = conn.cursor()
    
    # Create tables

    #ORGANIZATION
    cur.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            organization_id TEXT PRIMARY KEY,
            parent_id TEXT,
            organization_name TEXT,
            address TEXT,
            city TEXT,
            zipCode TEXT,
            state TEXT,
            country TEXT,
            FOREIGN KEY (parent_id) REFERENCES organizations(organization_id)
        )""")

    #MERCHANT
    cur.execute("""
        CREATE TABLE IF NOT EXISTS merchants (
            merchant_id TEXT PRIMARY KEY,
            organization_id TEXT,
            merchant_name TEXT,
            address TEXT,
            city TEXT,
            zipCode TEXT,
            state TEXT,
            country TEXT,
            merchant_category_code TEXT,
            FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
        )""")

    #LOGICAL_DEVICE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            merchant_id TEXT,
            device_name TEXT,
            device_reference TEXT,
            FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
        )""")
    
    #DEPLOYMENT
    cur.execute("""
        CREATE TABLE IF NOT EXISTS device_updates (
            deployment_id TEXT PRIMARY KEY,
            device_id TEXT,
            deployment_name TEXT,
            status TEXT,
            FOREIGN KEY (device_id) REFERENCES devices(device_id)
        )""")

    #TRANSACTION
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            merchant_name TEXT,
            device_reference TEXT,
            payment_type,
            transaction_value,
            FOREIGN KEY (merchant_name) REFERENCES merchants(merchant_name),
            FOREIGN KEY (device_reference) REFERENCES devices(device_reference)
        )""")

    conn.commit()

def load(event: dict, conn: sqlite3.Connection) -> str:

    # sql command parameters
    table_name = event['data_type']
    columns = ",".join(event['data'].keys())
    incognitas = ','.join(['?']*len(event['data'])) # to avoid sql injection

    try:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({incognitas})", list(event['data'].values()))
        conn.commit()
        print("Successfull insertion!")
    except sqlite3.Error as e:
        print("SQLite Error:", e)

def update(event: dict, conn: sqlite3.Connection) -> str:

    # sql command parameters
    table_name = event['data_type']
    update_command = ",".join([f"{col} = '{value}'" for col, value in event['data'].items() if value!=None]) # keep only columns to update
    column_id = event['data_type'][:-1]+'_id'
    id = event['data'][column_id]

    try:
        cur = conn.cursor()
        cur.execute(f"UPDATE {table_name} SET {update_command} WHERE {column_id} = '{id}'")
        conn.commit()
        print("Successfull update!")
    except sqlite3.Error as e:
        print("SQLite Error:", e)

def delete(event: dict, conn: sqlite3.Connection) -> str:

    # sql command parameters
    table_name = event['data_type']
    column_id = list(event['data'].keys())[0]
    id = list(event['data'].values())[0]

    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table_name} WHERE {column_id} = '{id}'")
        conn.commit()
        print("Successfull deletion!")
    except sqlite3.Error as e:
        print("SQLite Error:", e)