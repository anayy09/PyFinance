import sqlite3
import pandas as pd

def create_database(db_file):
    """
    Create SQLite database and table to store stock data.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            Ticker TEXT,
            Date DATE,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Adj_Close REAL,
            Volume INTEGER,
            SMA_20 REAL,
            EMA_20 REAL,
            Bollinger_Upper REAL,
            Bollinger_Lower REAL,
            RSI_14 REAL,
            PRIMARY KEY (Ticker, Date)
        )
    ''')
    conn.commit()
    conn.close()

def insert_data(df, db_file='stock_data.db'):
    """
    Insert transformed data into the SQLite database.
    """
    with sqlite3.connect(db_file) as conn:
        try:
            df.to_sql('stock_data', conn, if_exists='append', index=False)
        except Exception as e:
            print("An error occurred:", e)
            # Rollback is handled automatically if an exception occurs

def query_data(ticker, db_file='stock_data.db'):
    """
    Query and return data for a specific ticker from the SQLite database.
    """
    conn = sqlite3.connect(db_file)
    query = "SELECT * FROM stock_data WHERE Ticker = ?"
    df = pd.read_sql_query(query, conn, params=(ticker,))
    conn.close()
    return df

# Example Usage (Uncomment to use)
# create_database('stock_data.db')  # Ensure the database & table exists

# Example of how to call insert_data
# insert_data(data_transformed)

# Example of querying data
# print(query_data('AAPL').head())
