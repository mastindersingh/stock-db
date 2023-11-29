from flask import Flask, render_template, request, redirect, url_for, session
import os
from db import read_stock_purchases, write_stock_purchases, get_user_id, verify_user, create_user
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from decimal import Decimal
import pandas as pd
import logging
from dotenv import load_dotenv
load_dotenv('.env.development.local')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-default-secret-key')


@app.route('/user-portfolio', methods=['GET', 'POST'])
def user_portfolio():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    if not user_id:
        print("User ID not found in session. Redirecting to login.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        ticker = request.form.get('ticker')
        buy_date = request.form.get('buy_date')
        buy_price = request.form.get('buy_price')
        quantity = request.form.get('quantity')

        buy_price = Decimal(buy_price)
        quantity = int(quantity)

        new_stock_data = pd.DataFrame({
            'Ticker': [ticker],
            'BuyDate': [buy_date],
            'BuyPrice': [buy_price],
            'Quantity': [quantity]
        })

        write_stock_purchases(user_id, new_stock_data)

    stock_data = fetch_stock_data(read_stock_purchases(user_id))
    return render_template('user_portfolio.html', stock_data=stock_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if verify_user(email, password):
            session['logged_in'] = True
            session['email'] = email
            user_id = get_user_id(email)  # Get user_id from the database
            if user_id:
                session['user_id'] = user_id  # Set user_id in session
                print(session)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Add logic to validate the input data
        create_user(email, password)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    if not user_id:
        # Handle the case where user_id is not found - perhaps redirect to login
        print("User ID not found in session. Redirecting to login.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle POST request logic here
        pass

    # Fetch stock data for the logged-in user
    stock_data = fetch_stock_data(read_stock_purchases(user_id))
    return render_template('stocks.html', stock_data=stock_data)






@app.route('/stocks', methods=['POST'])
def add_stock():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    if not user_id:
        print("User ID not found in session. Redirecting to login.")
        return redirect(url_for('login'))

    ticker = request.form.get('ticker')
    buy_date = request.form.get('buy_date')
    buy_price = request.form.get('buy_price')
    quantity = request.form.get('quantity')
    print(f"Received data: {ticker}, {buy_date}, {buy_price}, {quantity}")

    buy_price = Decimal(buy_price)
    quantity = int(quantity)

    new_stock_data = pd.DataFrame({
        'Ticker': [ticker],
        'BuyDate': [buy_date],
        'BuyPrice': [buy_price],
        'Quantity': [quantity]
    })

    write_stock_purchases(user_id, new_stock_data)

    # Fetch the updated stock purchases DataFrame
    updated_stock_purchases_df = read_stock_purchases(user_id)
    stock_data = fetch_stock_data(updated_stock_purchases_df)

    return render_template('stocks.html', stock_data=stock_data)



def fetch_stock_data(stock_purchases):
    stock_data = {}
    for ticker, group in stock_purchases.groupby('Ticker'):
        total_quantity = group['Quantity'].sum()
        weighted_avg_price = Decimal((group['BuyPrice'] * group['Quantity']).sum()) / Decimal(int(total_quantity))
        tickerData = yf.Ticker(ticker)
        data = tickerData.history(period="max")
        current_price = Decimal(data['Close'].iloc[-1])
        percentage_change = ((current_price - weighted_avg_price) / weighted_avg_price) * 100
        performance = "Up" if current_price > weighted_avg_price else "Down"
        #logging.basicConfig(level=logging.DEBUG)
        #logging.debug(f"Stock data for {ticker}: {stock_data[ticker]}")
        plt.figure(figsize=(10, 4))
        plt.plot(data['Close'])
        plt.title(f"{ticker} Stock Price")
        plt.xlabel("Date")
        plt.ylabel("Price")
        graph = get_graph()

        stock_data[ticker] = {
            'data': data,
            'earliest_buy_date': group['BuyDate'].min(),
            'weighted_avg_price': weighted_avg_price,
            'total_quantity': total_quantity,
            'current_price': current_price,
            'performance': performance,
            'percentage_change': percentage_change,
            'graph': graph
        }

    return stock_data

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

if __name__ == '__main__':
    app.run(debug=True)

