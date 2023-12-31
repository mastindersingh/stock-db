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
#from flask_oauthlib.client import OAuth
#from authlib.integrations.flask_client import OAuth
#from models import User
import binascii
from authlib.integrations.flask_client import OAuth
# Configure Matplotlib
matplotlib.use('Agg')
 
app = Flask(__name__)
app.secret_key = os.environ.get('bApG1HXBfOeC5JhRj_tvKA', 'your-default-secret-key')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://default:QhYas0zXyE7A@ep-royal-thunder-45099107-pooler.us-east-1.postgres.vercel-storage.com:5432/verceldb'
#db.init_app(app)


oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id='72321166098-1kb2nesvub2drdp6dqhmjir92uei1sce.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/authorized')
def authorized():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    user_id = get_user_id(user_info['email'])
    if not user_id:
       # user_id = create_user(user_info['email'], os.urandom(24))  # Random password
         user_id = create_user(user_info['email'], binascii.hexlify(os.urandom(24)).decode())  # Random password
    session['logged_in'] = True
    session['user_id'] = user_id
    session['email'] = user_info['email']
    return redirect(url_for('user_portfolio'))


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


#oauth = OAuth(app)

# Google OAuth Configuration with Authlib
#google = oauth.register(
#    name='google',
    #client_id='72321166098-1kb2nesvub2drdp6dqhmjir92uei1sce.apps.googleusercontent.com',
    #client_secret='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',
 #   client_id='72321166098-rqs54h296h3pp6clb1h19cn7bp4rp8rn.apps.googleusercontent.com',
 #   client_secret='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',
 #   access_token_url='https://accounts.google.com/o/oauth2/token',
 #   authorize_url='https://accounts.google.com/o/oauth2/auth',
 #   api_base_url='https://www.googleapis.com/oauth2/v1/',
 #   client_kwargs={'scope': 'email'}i)

#def google_login():
#    return google.authorize(callback=url_for('authorized', _external=True))


#@app.route('/login/authorized')
#def authorized():
#    token = google.authorize_access_token()
#    user_info = google.get('userinfo').json()

    # Example: Check if user exists in your database
#    user = User.query.filter_by(email=user_info['email']).first()
#    if not user:
        # User doesn't exist, so create a new user
#        user = User(email=user_info['email'])
#        db.session.add(user)
#        db.session.commit()

    # Set user information in session
#    session['user_id'] = user.id
#    session['email'] = user.email

    # Redirect to a dashboard or home page
#    return redirect(url_for('dashboard'))
#@app.route('/google-login')
#def google_login():
#    redirect_uri = url_for('authorized', _external=True)
#    return google.authorize_redirect(redirect_uri)


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

