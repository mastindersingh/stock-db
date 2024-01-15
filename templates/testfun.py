import yfinance as yf
import pandas as pd



def test_financial_data(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.T
    balance_sheet = stock.balance_sheet.T

    print(f"Financial Data for {ticker}:")
    print("Net Income:")
    print(financials.get('Net Income', pd.Series()))

    print("\nBalance Sheet Column Names:")
    print(balance_sheet.columns)  # Print all column names in the balance sheet

    total_stockholder_equity = balance_sheet.get('Total Stockholder Equity', pd.Series())
    print("\nTotal Stockholder Equity:")
    print(total_stockholder_equity)

test_ticker = 'RELIANCE.NS'
test_financial_data(test_ticker)

