from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StockPurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(50), nullable=False)
    buy_date = db.Column(db.Date, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

