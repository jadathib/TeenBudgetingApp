from models import Transactions
from sqlalchemy import exc, desc


# Find milestone for first savings deposit
def firstDay(username):
    firstDate = Transactions.query.filter_by(username=username, purpose='deposit', ).order_by(Transactions.date.desc()).all()[-1]
    return firstDate.date

# Find milestone for first $50 in savings
def first50(username):
    validTransactions = Transactions.query.filter_by(username=username, purpose='deposit').order_by(Transactions.date.desc()).all()[::-1]
    totalSavings = 0
    for transaction in validTransactions:
        percentage = transaction.savingPercent / 100
        amountToAdd = transaction.amount * percentage
        totalSavings = totalSavings + amountToAdd
        if totalSavings >= 50 and totalSavings < 100:
            return transaction.date
    
    return "Milestone not yet reached"
        # Keep track of total savings until you hit milestone, then return that date you hit it

# Find milestone for first $100 in savings
def first100(username):
    validTransactions = Transactions.query.filter_by(username=username, purpose='deposit').order_by(Transactions.date.desc()).all()[::-1]
    totalSavings = 0
    for transaction in validTransactions:
        percentage = transaction.savingPercent / 100
        amountToAdd = transaction.amount * percentage
        totalSavings = totalSavings + amountToAdd
        if totalSavings >= 100 and totalSavings < 200:
            return transaction.date

    return "Milestone not yet reached"

# Find milestone for first $200 in savings
def first200(username):
    validTransactions = Transactions.query.filter_by(username=username, purpose='deposit').order_by(Transactions.date.desc()).all()[::-1]
    totalSavings = 0
    for transaction in validTransactions:
        percentage = transaction.savingPercent / 100
        amountToAdd = transaction.amount * percentage
        totalSavings = totalSavings + amountToAdd
        if totalSavings >= 200:
            return transaction.date

    return "Milestone not yet reached"



# Get ALL milestones, format: DATE
def getMilestones(Username):
    milestoneList = []
    milestoneList.append(firstDay(Username))
    milestoneList.append(first50(Username))
    milestoneList.append(first100(Username))
    milestoneList.append(first200(Username))
    return milestoneList