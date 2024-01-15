import yfinance as yf
import pandas as pd
import numpy as np


def analyze_nifty_stocks(tickers, start_date, end_date):
    results = pd.DataFrame()

    for ticker in tickers:
        try:
            print(f"Fetching data for {ticker}...")
            stock = yf.Ticker(ticker)
            stock_data = stock.history(start=start_date, end=end_date)

            # Using 'Close' column directly
            print(f"Processing data for {ticker}...")
            CAGR, pe_ratio, roe, debt_to_equity = calculate_financial_metrics(stock, stock_data, 'Close')

            stock_data['50_MA'] = stock_data['Close'].rolling(window=50).mean()
            stock_data['200_MA'] = stock_data['Close'].rolling(window=200).mean()
            stock_data['RSI'] = compute_rsi(stock_data['Close'])

            latest_50_MA = stock_data['50_MA'].iloc[-1]
            latest_200_MA = stock_data['200_MA'].iloc[-1]
            latest_RSI = stock_data['RSI'].iloc[-1]

            results = results.append({'Ticker': ticker,
                                      'Annual Growth Rate': CAGR,
                                      'P/E Ratio': pe_ratio,
                                      'Return on Equity': roe,
                                      'Debt to Equity': debt_to_equity,
                                      '50-Day MA': latest_50_MA,
                                      '200-Day MA': latest_200_MA,
                                      'RSI': latest_RSI},
                                     ignore_index=True)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    return results




def calculate_financial_metrics(stock, stock_data):
    initial_price = stock_data['Adj Close'].iloc[0]
    final_price = stock_data['Adj Close'].iloc[-1]
    years = (stock_data.index[-1] - stock_data.index[0]).days / 365.25
    CAGR = ((final_price / initial_price) ** (1 / years)) - 1

    financials = stock.financials
    balance_sheet = stock.balance_sheet

    pe_ratio = stock.info['trailingPE'] if 'trailingPE' in stock.info else 'N/A'
    roe = financials.loc['Net Income'] / balance_sheet.loc['Total Stockholder Equity']
    debt_to_equity = balance_sheet.loc['Total Debt'] / balance_sheet.loc['Total Stockholder Equity']

    return CAGR, pe_ratio, roe.iloc[-1], debt_to_equity.iloc[-1]

def compute_rsi(data, period=14):
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)

    ma_up = up.rolling(window=period).mean()
    ma_down = down.rolling(window=period).mean()

    rs = ma_up / ma_down
    RSI = 100 - (100 / (1 + rs))

    return RSI

# Example tickers from Nifty
nifty_tickers = ['INFY.NS']

# Analysis period
start_date = '2020-01-01'
end_date = '2023-01-01'

# Perform analysis
nifty_analysis = analyze_nifty_stocks(nifty_tickers, start_date, end_date)
print(nifty_analysis)

