import time
import pytest
import pandas as pd
from data_pipeline import calculate_sma, calculate_ema, calculate_rsi
from db_operations import create_database, insert_data, query_data
import pandas as pd
import os

# TASK 4
print("\nTASK 4\n")

# Sample data for testing
data = {
    'Close': [120, 121, 122, 123, 124, 125, 126, 127, 128, 129]
}
df = pd.DataFrame(data)

def test_calculate_sma():
    sma = calculate_sma(df['Close'], window=5)
    assert sma.iloc[-1] == 127  # Checking if the last SMA value is correct

def test_calculate_ema():
    ema = calculate_ema(df['Close'], window=5)
    # EMA calculations involve more complexity, so here we're checking if it's calculated (not NaN)
    assert not ema.isnull().any()

def test_calculate_rsi():
    rsi = calculate_rsi(df['Close'], window=14)
    # RSI should be between 0 and 100
    assert rsi.between(0, 100).all()

# Define the path to the temporary database
TEST_DB = 'test_stock_data.db'

def setup_function(function):
    # Create a new database for testing
    create_database(TEST_DB)


def teardown_function(function):
    retry_count = 3
    while retry_count > 0:
        try:
            if os.path.exists(TEST_DB):
                os.remove(TEST_DB)
            break
        except PermissionError:
            time.sleep(1)  # Wait for 1 second before retrying
            retry_count -= 1

def test_insert_and_query_data():
    # Create a small DataFrame to insert
    test_data = pd.DataFrame({
        'Ticker': ['AAPL'],
        'Date': ['2023-01-01'],
        'Open': [150.0],
        'High': [155.0],
        'Low': [149.0],
        'Close': [154.0],
        'Adj_Close': [154.0],
        'Volume': [100000],
        'SMA_20': [153.0],
        'EMA_20': [153.5],
        'Bollinger_Upper': [160.0],
        'Bollinger_Lower': [146.0],
        'RSI_14': [70.0]
    })

    # Insert data into the test database
    insert_data(test_data, TEST_DB)

    # Query data back to verify insertion
    queried_data = query_data('AAPL', TEST_DB)

    # Verify that the DataFrame is not empty and contains the inserted data
    assert not queried_data.empty
    assert queried_data.iloc[0]['Ticker'] == 'AAPL'
    assert queried_data.iloc[0]['Close'] == 154.0