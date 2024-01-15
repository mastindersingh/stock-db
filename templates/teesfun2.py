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

    # Retrieve 'Net Income' and 'Total Stockholder Equity'
    net_income = financials.get('Net Income', pd.Series())
    shareholders_equity = balance_sheet.get('Stockholders Equity', pd.Series())

    # Calculate ROE (Return on Equity)
    if not net_income.empty and not shareholders_equity.empty:
        roe = net_income.iloc[0] / shareholders_equity.iloc[0] if shareholders_equity.iloc[0] != 0 else 'N/A'
    else:
        roe = 'N/A'

    # Calculate ROCE (Return on Capital Employed)
    ebit = financials.get('Ebit', pd.Series())
    total_assets = balance_sheet.get('Total Assets', pd.Series())
    current_liabilities = balance_sheet.get('Total Current Liabilities', pd.Series())

    if not ebit.empty and not total_assets.empty and not current_liabilities.empty:
        capital_employed = total_assets.iloc[0] - current_liabilities.iloc[0]
        roce = ebit.iloc[0] / capital_employed if capital_employed != 0 else 'N/A'
    else:
        roce = 'N/A'

    return {'ROE': roe, 'ROCE': roce}

def fetch_additional_metrics(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)

    # Example metrics
    pe_ratio = stock.info.get('trailingPE', 'N/A')
    price_to_book = stock.info.get('priceToBook', 'N/A')
    peg_ratio = stock.info.get('pegRatio', 'N/A')
    dividend_yield = stock.info.get('dividendYield', 'N/A')

    return {'PE Ratio': pe_ratio, 'Price to Book': price_to_book, 'PEG Ratio': peg_ratio, 'Dividend Yield': dividend_yield}

# Example usage
ticker = 'AAPL'
start_date = '2020-01-01'
end_date = '2023-01-01'

# Analyze stock
stock_data = analyze_stock(ticker, start_date, end_date)
fundamentals = analyze_stock_fundamentals(ticker)
additional_metrics = fetch_additional_metrics(ticker)

# Print the first few rows of the stock data (technical analysis)
print("Technical Analysis Data:")
print(stock_data.head())

# Print the fundamental analysis data
print("\nFundamental Analysis Data:")
for key, value in fundamentals.items():
    print(f"{key}: {value}")

for key, value in additional_metrics.items():
    print(f"{key}: {value}")

# Plotting the closing prices and moving averages
plt.figure(figsize=(12, 6))
plt.plot(stock_data['Close'], label='Closing Price')
plt.plot(stock_data['50-Day MA'], label='50-Day Moving Average')
plt.plot(stock_data['200-Day MA'], label='200-Day Moving Average')
plt.title(f'{ticker} Stock Price and Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

