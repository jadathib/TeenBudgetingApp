from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    checkingBalance = db.Column(db.Float, default=0.0)
    savingBalance = db.Column(db.Float, default=0.0)

    # Relationship (not required but nice)
    transactions = db.relationship("Transactions", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Transactions(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey("users.username"), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)  # deposit / withdrawal
    amount = db.Column(db.Float, nullable=False)
    savingPercent = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Transaction {self.purpose} {self.amount}>"
