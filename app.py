import logging

logging.basicConfig(level=logging.DEBUG)
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from db import delete_stock, get_subscription_code_for_user, update_subscription_code, read_stock_purchases, write_stock_purchases, get_user_id, verify_user, create_user, verify_subscription_code
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
from flask_mail import Mail, Message
from requests.exceptions import HTTPError
from models import BlogPost
from lesson import lessons
import yfinance.exceptions as yf_exceptions
from pandas_datareader import data as pdr
yf.pdr_override()


#from flask_oauthlib.client import OAuth
#from authlib.integrations.flask_client import OAuth
#from models import User
import binascii
from authlib.integrations.flask_client import OAuth
# Configure Matplotlib
matplotlib.use('Agg')
from authlib.integrations.base_client.errors import OAuthError  # Add this import 
app = Flask(__name__)
app.secret_key = os.environ.get('bApG1HXBfOeC5JhRj_tvKA', 'your-default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://default:QhYas0zXyE7A@ep-royal-thunder-45099107-pooler.us-east-1.postgres.vercel-storage.com:5432/verceldb'
#db.init_app(app)
from authlib.integrations.base_client.errors import OAuthError  # Add this import
import uuid  # Add this import at the beginning of your script

app.config['SESSION_COOKIE_SECURE'] = False

#oauth = OAuth(app)

#google = oauth.register(
    #name='google',
    #client_id='72321166098-rqs54h296h3pp6clb1h19cn7bp4rp8rn.apps.googleusercontent.com',
    #client_secret='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',
    #access_token_url='https://accounts.google.com/o/oauth2/token',
    #authorize_url='https://accounts.google.com/o/oauth2/auth',
    #api_base_url='https://www.googleapis.com/oauth2/v1/',
    #jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    #client_kwargs={'scope': 'openid email profile'},
#)

#@app.route('/login/google')
#def login_google():
    #redirect_uri = url_for('authorized', _external=True)
    #return google.authorize_redirect(redirect_uri)

def get_stock_recommendations():
    # Replace this with actual logic to fetch data from your database
    return [
        {'name': 'Apple Inc', 'price': 150, 'recommendation': 'Buy'},
        {'name': 'Microsoft Corp', 'price': 250, 'recommendation': 'Hold'}
    ]


@app.route('/blog')
def blog():
    posts = BlogPost.get_all_posts()  # Use the static method to fetch all blog posts
    return render_template('blog.html', posts=posts)

@app.route('/video_gallery')
def video_gallery():
    return render_template('video_gallery.html')

@app.route('/lessons')
def show_lessons():
    return render_template('lessons.html', lessons=lessons)


@app.route('/master-portfolio')
def master_portfolio():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_email = session.get('email')
    subscription_code = session.get('subscription_code')  # Retrieve the code from the session

    # Check if the user has a valid subscription
    if not verify_subscription_code(user_email, subscription_code):
        # If not, redirect to the subscription page
        return redirect(url_for('subscribe'))

    # Fetch the user ID for mastinder@yahoo.com
    master_user_id = get_user_id('mastinder@yahoo.com')
    if master_user_id is None:
        return "Master user not found", 404

    # Fetch the stock data for the master user
    master_stock_data = fetch_stock_data(read_stock_purchases(master_user_id))

    return render_template('master_portfolio.html', stock_data=master_stock_data)




# Configure email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Set your email
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Set your email password

mail = Mail(app)

# ... existing routes ...

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Create and send the email
        msg = Message("New Contact Form Submission",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[app.config['MAIL_USERNAME']],  # Email to send to
                      body=f"Name: {name}\nEmail: {email}\nMessage: {message}")
        mail.send(msg)

        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')








@app.route('/search_stock', methods=['GET', 'POST'])
def search_stock():
    stock_info = None

    if request.method == 'POST':
        query = request.form.get('query')

        if not query:
            flash("Please enter a stock symbol.", "danger")
        else:
            try:
                # Create a stock object using yfinance
                stock = yf.Ticker(query)
                stock_info = stock.info

                # Check if the stock information is valid
                if stock_info and 'regularMarketPrice' in stock_info:
                    # Additional data fetching
                    hist = stock.history(period="1mo")
                    actions = stock.actions
                    dividends = stock.dividends
                    splits = stock.splits
                    financials = stock.financials
                    major_holders = stock.major_holders
                    institutional_holders = stock.institutional_holders
                    earnings_dates = stock.earnings_dates
                    isin = stock.isin if 'isin' in stock_info else 'N/A'
                    options = stock.options
                    news = stock.news

                    # Combine all data into stock_info
                    stock_info.update({
                        'history': hist.to_dict(),
                        'actions': actions.to_dict(),
                        'dividends': dividends.to_dict(),
                        'splits': splits.to_dict(),
                        'financials': financials.to_dict(),
                        'major_holders': major_holders,
                        'institutional_holders': institutional_holders,
                        'earnings_dates': earnings_dates,
                        'isin': isin,
                        'options': options,
                        'news': news
                    })

                    return render_template('user_portfolio.html', stock_info=stock_info)
                else:
                    flash(f"Stock symbol '{query}' not found.", "danger")

            except Exception as e:  # Catching a general exception
                flash(f"An error occurred: {e}", "danger")

    return render_template('user_portfolio.html', stock_info=stock_info)










@app.route('/stock_info')
def stock_info():
    query = request.args.get('symbol')

    if not query:
        flash("No stock symbol provided.", "danger")
        return redirect(url_for('search_stock'))

    try:
        stock = yf.Ticker(query)
        stock_info = stock.info

        if stock_info and 'regularMarketPrice' in stock_info:
            # Fetch additional data
            hist = stock.history(period="1mo")
            actions = stock.actions
            dividends = stock.dividends
            splits = stock.splits
            financials = stock.financials
            major_holders = stock.major_holders
            institutional_holders = stock.institutional_holders
            earnings_dates = stock.earnings_dates
            isin = stock.isin if 'isin' in stock_info else 'N/A'
            options = stock.options
            news = stock.news

            # Combine all data into stock_info
            stock_info.update({
                'history': hist.to_dict(),
                'actions': actions.to_dict(),
                'dividends': dividends.to_dict(),
                'splits': splits.to_dict(),
                'financials': financials.to_dict(),
                'major_holders': major_holders,
                'institutional_holders': institutional_holders,
                'earnings_dates': earnings_dates,
                'isin': isin,
                'options': options,
                'news': news
            })

            return render_template('stock_info.html', stock_info=stock_info)
        else:
            flash(f"Stock symbol '{query}' not found.", "danger")
    except HTTPError:
        flash(f"Stock symbol '{query}' not found.", "danger")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")

    return redirect(url_for('search_stock'))








@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        subscription_code = request.form['subscription_code']
        user_id = session.get('user_id')

        if user_id and verify_subscription_code(session.get('email'), subscription_code):
            update_subscription_code(user_id, subscription_code)
            session['subscription_code'] = subscription_code  # Store the code in the session
            return redirect(url_for('master_portfolio'))
        else:
            return render_template('subscribe.html', error="Invalid subscription code.")

    return render_template('subscribe.html')



@app.route('/Aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/delete_stock', methods=['POST'])
def delete_stock_route():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    if not user_id:
        flash("User ID not found in session. Redirecting to login.", "warning")
        return redirect(url_for('login'))

    ticker = request.form.get('ticker')
    if ticker:
        try:
            # Assuming delete_stock function is imported from db.py
            delete_stock(ticker)
            flash(f"Stock with ticker '{ticker}' has been deleted.", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
    else:
        flash("No ticker provided for deletion.", "warning")

    return redirect(url_for('user_portfolio'))



#@app.route('/master-portfolio')
#def master_portfolio():
    #if 'logged_in' not in session:
     #   return redirect(url_for('login'))
    #user_id = session.get('user_id')
    # Check if the user has a valid subscription
   # if not verify_subscription_code(session.get('email')):
        # If not, redirect to the subscription page
    #    return redirect(url_for('subscribe'))
    # Fetch the user ID for mastinder@yahoo.com
   # master_user_id = get_user_id('mastinder@yahoo.com')
   # if master_user_id is None:
    #    return "Master user not found", 404
    # Fetch the stock data for the master user
   # master_stock_data = fetch_stock_data(read_stock_purchases(master_user_id))
   # return render_template('master_portfolio.html', stock_data=master_stock_data)




@app.route('/user-portfolio', methods=['GET', 'POST'])
def user_portfolio():
    if 'logged_in' not in session or 'user_id' not in session:
        app.logger.warning("User ID not found in session. Redirecting to login.")
        return redirect(url_for('login'))

    # Rest of your code...

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

#@app.route('/', methods=['GET', 'POST'])
#def index():
#    if 'logged_in' not in session:
#        return redirect(url_for('login'))

#    user_id = session.get('user_id')
#    if not user_id:
#        # Handle the case where user_id is not found - perhaps redirect to login

#        print("User ID not found in session. Redirecting to login.")
#        return redirect(url_for('login'))

#    if request.method == 'POST':
        # Handle POST request logic here
#        pass

    # Fetch stock data for the logged-in user

#    stock_data = fetch_stock_data(read_stock_purchases(user_id))
#    return render_template('stocks.html', stock_data=stock_data)



@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    if not user_id:
        print("User ID not found in session. Redirecting to login.")
        return redirect(url_for('login'))

    return redirect(url_for('user_portfolio'))




# Google OAuth Setup

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='995479100873-lv8vmhh52pg54k6smle00t4k3cihvm5p.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email profile'})







@app.route('/google-login')
def google_login():
    
    redirect_uri = url_for('authorized', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)



@app.route('/login/authorized')
def authorized():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo').json()
    
    user = get_google_user(user_info['email'])
    if not user:
        create_google_user(user_info['email'], user_info.get('id'))
        user = get_google_user(user_info['email']) 

    if user:
       logging.debug(f"User found: {user}")
       session['logged_in'] = True  # Indicate that the user is logged in
       session['user_id'] = user[0]
       session['email'] = user[1]
       logging.debug(f"Session set: {session}")
       return redirect(url_for('user_portfolio'))
    else:
       logging.debug("User not found.")
       flash('User not found. Please try logging in again.', 'error')
       return redirect(url_for('login'))


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

        # Check if the data DataFrame is empty
        if data.empty:
            print(f"No data found for {ticker}, symbol may be delisted or invalid.")
            continue  # Skip to the next ticker

        current_price = Decimal(data['Close'].iloc[-1])
        percentage_change = ((current_price - weighted_avg_price) / weighted_avg_price) * 100
        performance = "Up" if current_price > weighted_avg_price else "Down"

        plt.figure(figsize=(10, 4))
        plt.plot(data['Close'])
        plt.title(f"{ticker} Stock Price")
        plt.xlabel("Date")
        plt.ylabel("Price")
        graph = get_graph()
        plt.close()

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
    plt.close()
    return graph





if __name__ == '__main__':
    app.run(debug=True)
