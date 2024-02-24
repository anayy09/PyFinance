from db_operations import create_database, insert_data
import pandas as pd
import numpy as np
import yfinance as yf
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define the stocks to fetch data
stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "JNJ", "WMT", "V"]

# Fetch historical data for these stocks


def fetch_data(tickers):
    data = {}
    for ticker in tickers:
        data[ticker] = yf.download(
            ticker, start="2023-01-01", end="2023-12-31")
        # Basic validation check for missing values
        if data[ticker].isnull().values.any():
            print(f"Missing values detected in {ticker}")
        # Ensuring data type consistency
        if not all(isinstance(x, float) for x in data[ticker].select_dtypes(include=['float']).iloc[0]):
            print(f"Data type inconsistency detected in {ticker}")
    return data


# TASK 1
print("\nTASK 1\n")

# Standardize and validate the data
data = fetch_data(stocks)

# Convert dictionary of DataFrames to a single DataFrame with MultiIndex
data_combined = pd.concat(
    data.values(), keys=data.keys(), names=['Ticker', 'Date'])

print(data_combined.head())

# TASK 2
print("\nTASK 2\n")

# Updated Outlier Removal Function


def remove_outliers(df, threshold=3):
    for column in df.select_dtypes(include=['float64', 'int64']).columns:
        df_column = df[column]
        mean = df_column.mean()
        std = df_column.std()
        z_scores = (df_column - mean) / std
        # Replace outliers with NaN
        df[column] = df_column.where(np.abs(z_scores) <= threshold, np.nan)
    return df.ffill()  # Forward fill to handle NaNs created by outlier removal without warnings


# Apply the function without future warnings
data_combined_cleaned = data_combined.groupby(
    level=0, group_keys=False).apply(remove_outliers)

# Ensuring Timestamp Consistency without using 'inplace'
data_combined_cleaned.index = data_combined_cleaned.index.set_levels(
    pd.to_datetime(data_combined_cleaned.index.levels[1]), level=1)

print(data_combined_cleaned.head())

# TASK 3
print("\nTASK 3\n")

# Calculate Simple Moving Average (SMA)


def calculate_sma(data, window=20):
    return data.rolling(window=window).mean()

# Calculate Exponential Moving Average (EMA)


def calculate_ema(data, window=20):
    return data.ewm(span=window, adjust=False).mean()

# Calculate Bollinger Bands


def calculate_bollinger_bands(data, window=20):
    sma = calculate_sma(data, window)
    std = data.rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band, lower_band

# Calculate Relative Strength Index (RSI)


def calculate_rsi(data, window=14):
    delta = data.diff(1)
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # Calculate the average gain and loss
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    # Calculate the RS
    rs = avg_gain / avg_loss

    # Calculate the RSI
    rsi = 100.0 - (100.0 / (1.0 + rs))

    # Replace initial NaN values with 0 for RSI calculation before enough data is available
    rsi = rsi.replace([np.inf, -np.inf], np.nan).fillna(0)

    return rsi

# Applying Transformations


def apply_transformations(data):
    for ticker, df in data.groupby(level='Ticker'):
        data.loc[ticker, 'SMA_20'] = calculate_sma(df['Close'], window=20)
        data.loc[ticker, 'EMA_20'] = calculate_ema(df['Close'], window=20)
        upper_band, lower_band = calculate_bollinger_bands(
            df['Close'], window=20)
        data.loc[ticker, 'Bollinger_Upper'] = upper_band
        data.loc[ticker, 'Bollinger_Lower'] = lower_band
        data.loc[ticker, 'RSI_14'] = calculate_rsi(df['Close'], window=14)
    return data


data_transformed = apply_transformations(data_combined_cleaned)

print(data_transformed.head())

# TASK 5
print("\nTASK 5\n")

# After renaming and before inserting
data_transformed.rename(columns={
    'Adj Close': 'Adj_Close'
}, inplace=True)

# In data_pipeline.py, before the insertion
data_transformed.reset_index(inplace=True)

# In data_pipeline.py, before the insertion
data_transformed['Date'] = pd.to_datetime(data_transformed['Date']).dt.date


# Ensure the database & table exists
create_database('stock_data.db')

# Insert the transformed data into the database
insert_data(data_transformed)

print(data_transformed.head())
# Gives the summary including non-null count to verify data completeness
print(data_transformed.info())
