import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def analyze_stock(ticker, start_date, end_date):
    # Download stock data
    stock_data = yf.download(ticker, start=start_date, end=end_date)

    # Calculate daily percentage change
    stock_data['Daily Change'] = stock_data['Close'].pct_change()

    # Calculate moving averages (50-day and 200-day)
    stock_data['50-Day MA'] = stock_data['Close'].rolling(window=50).mean()
    stock_data['200-Day MA'] = stock_data['Close'].rolling(window=200).mean()

    return stock_data

def analyze_stock_fundamentals(ticker):
    stock = yf.Ticker(ticker)

    # Fetching financials and balance sheet data
    financials = stock.financials.T
    balance_sheet = stock.balance_sheet.T

    # Check if financial data is available
    if financials.empty or balance_sheet.empty:
        print(f"Financial data not available for {ticker}")
        return None

    # Ensure that the required data is available
    net_income = financials.get('Net Income', pd.Series())
    shareholders_equity = balance_sheet.get('Total Stockholder Equity', pd.Series())

    if not net_income.empty and not shareholders_equity.empty:
        roe = net_income.iloc[0] / shareholders_equity.iloc[0] if shareholders_equity.iloc[0] != 0 else 'N/A'
    else:
        roe = 'N/A'

    # Similar checks for other calculations like ROCE
    # ...

    return {
        'ROE': roe
        # Add other metrics once calculated
    }

# Analyze RELIANCE.NS stock
ticker = 'RELIANCE.NS'
start_date = '2020-01-01'
end_date = '2023-01-01'
reliance_data = analyze_stock(ticker, start_date, end_date)
reliance_fundamentals = analyze_stock_fundamentals(ticker)

# Print the first few rows of the stock data (technical analysis)
print("Technical Analysis Data:")
print(reliance_data.head())

# Print the fundamental analysis data
print("\nFundamental Analysis Data:")
if reliance_fundamentals:
    for key, value in reliance_fundamentals.items():
        print(f"{key}: {value}")
else:
    print("Fundamental data not available.")

# Plotting the closing prices and moving averages
plt.figure(figsize=(12, 6))
plt.plot(reliance_data['Close'], label='Closing Price')
plt.plot(reliance_data['50-Day MA'], label='50-Day Moving Average')
plt.plot(reliance_data['200-Day MA'], label='200-Day Moving Average')
plt.title(f'{ticker} Stock Price and Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

