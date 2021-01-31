from flask import Flask, render_template,request, redirect
from cs50 import SQL

app = Flask(__name__)

# Initialization of database
db = SQL('sqlite:///userbalances.db')

# Database schema is as shown
'''
    Table Name: transactions
    Columns: amount     date        type        savingPercent
    Datatype: Real   Integer     Integer        Real
    Explanation:
        Amount is stored as a real (floating point) number
        Date is stored as an integer representing the date & time in unix time (easier to convert it to local time if stored as unix epoch or utc?)
        Type is stored as an integer of 0 or 1 to represent boolean values (sqlite doesn't have native boolean data type) 0 means deposit & 1 means withdrawal
        savingPercent is stored as a real (floating point) number that should be between 0.1 & 1 (check this in logic)
'''

@app.route('/')
def index():
    print("Home Page")
    return render_template('index.html')


@app.route('/checking')
def checking():
    print("Query for checking balance from database")
    return render_template('checking.html')

@app.route('/savings')
def savings():
    print("Query for savings balance from database")
    return render_template('savings.html')

@app.route('/transactions')
def transactions():
    print("Quary for transaction date")
    print("Quary for transaction amount")
    print("Quary for transaction catagory")
    return render_template('transactions.html')

@app.route('/deposits')
def modifyDeposits():
    return render_template('deposits.html')

@app.route('/expenses')
def modifyExpenses():
    return render_template('expenses.html')