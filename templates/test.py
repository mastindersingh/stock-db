import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Function to download and analyze stock data
def analyze_stock(ticker, start_date, end_date):
    # Download stock data
    stock_data = yf.download(ticker, start=start_date, end=end_date)

    # Calculate daily percentage change
    stock_data['Daily Change'] = stock_data['Close'].pct_change()

    # Calculate moving averages (50-day and 200-day)
    stock_data['50-Day MA'] = stock_data['Close'].rolling(window=50).mean()
    stock_data['200-Day MA'] = stock_data['Close'].rolling(window=200).mean()

    return stock_data

# Analyze RELIANCE.NS stock
ticker = 'RELIANCE.NS'
start_date = '2020-01-01'
end_date = '2023-01-01'
reliance_data = analyze_stock(ticker, start_date, end_date)

# Print first few rows of the data
print(reliance_data.head())

# Plot the closing prices
plt.figure(figsize=(10, 6))
plt.plot(reliance_data['Close'], label='Closing Price')
plt.plot(reliance_data['50-Day MA'], label='50-Day MA')
plt.plot(reliance_data['200-Day MA'], label='200-Day MA')
plt.title(f'{ticker} Stock Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

