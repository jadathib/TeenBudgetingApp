from models import Transactions
from sqlalchemy import exc, desc

# Find milestone for first savings deposit
def firstDay(Transactions_tb):
    pass

# Find milestone for first $50 in savings
def first50(Transactions_tb):
    validTransactions = Transactions_tb.query.filter_by(purpose='deposit').order_by(Transactions.date.desc()).all()
    for transaction in validTransactions:
        pass
        # Keep track of total savings until you hit milestone, then return that date you hit it
    pass
# Find milestone for first $100 in savings
def first100(Transactions_tb):
    pass
# Find milestone for first $200 in savings
def first200(Transactions_tb):
    pass



# Get ALL milestones, format: DATE
def getMilestones(Transactions_tb):
    milestoneList = []
    milestoneList.append(firstDay(Transactions_tb))
    milestoneList.append(first50(Transactions))
    milestoneList.append(first100(Transactions))
    milestoneList.append(first200(Transactions))
    return milestoneList