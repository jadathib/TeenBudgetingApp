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

@app.route('/checking', methods=["GET","POST"])
def checking():

    if request.method=="GET":
        allTransactions = db.execute("SELECT * FROM transactions")

        totalBal = 0
        for transaction in allTransactions:
            if transaction['type'] == 'deposit':
                totalBal += transaction['amount']
        return render_template('checking.html')
    else:
        return redirect('/modifybalance')

@app.route('/savings', methods=["GET","POST"])
def savings():
    return "Savings Account Page"

@app.route('/spendingcategory')
def category():
    return "Spending Category Page"

@app.route('/modifybalance')
def modifybalance():
    return render_template('modifybalance.html')
