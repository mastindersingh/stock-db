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

    # Calculate ROE (Return on Equity)
    if 'Net Income' in financials and 'Total Stockholder Equity' in balance_sheet:
        net_income = financials['Net Income'].iloc[0]
        shareholders_equity = balance_sheet['Total Stockholder Equity'].iloc[0]
        roe = net_income / shareholders_equity if shareholders_equity != 0 else 'N/A'
    else:
        roe = 'N/A'

    # Other calculations (ROCE, P/E Ratio, EPS) can be added here in a similar manner
    # ...

    return {
        'ROE': roe
        # Include other metrics once calculated
    }




# Analyze RELIANCE.NS stock
ticker = 'RELIANCE.NS'
start_date = '2020-01-01'
end_date = '2023-01-01'
reliance_data = analyze_stock(ticker, start_date, end_date)
reliance_fundamentals = analyze_stock_fundamentals(ticker)

# Print first few rows of the data and the fundamentals
print(reliance_data.head())
print(f"Fundamentals for {ticker}:")
print(reliance_fundamentals)

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

