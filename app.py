from flask import Flask, render_template, request, redirect, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Transactions
from milestones import getMilestones  # assuming you built this

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userbalances.db'
app.config['SECRET_KEY'] = b'\x1bt!"e\xf7)Q5\xebz"f\xfa\xe6K'

# Init login manager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Init database
db.init_app(app)


# -------------------------
# Routes
# -------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/checking', methods=["GET", "POST"])
@login_required
def checking():
    if request.method == "GET":
        return render_template('checking.html',
                               checkBalance=current_user.checkingBalance)
    return redirect('/')


@app.route('/savings', methods=["GET", "POST"])
@login_required
def savings():
    if request.method == "GET":
        firstSavingsDate = Transactions.query.filter_by(
            username=current_user.username
        ).order_by(Transactions.date.asc()).first()
        lastSavingsDate = Transactions.query.filter_by(
            username=current_user.username
        ).order_by(Transactions.date.desc()).first()

        milestones = getMilestones(current_user.username)
        return render_template('savings.html',
                               firstSavingsDate=firstSavingsDate,
                               lastSavingsDate=lastSavingsDate,
                               savingBalance=current_user.savingBalance,
                               milestones=milestones)
    return redirect('/')


@app.route('/transactions', methods=["GET", "POST"])
@login_required
def transactions():
    transactionsToDisplay = Transactions.query.filter_by(
        username=current_user.username
    ).order_by(Transactions.date.desc()).all()
    return render_template('transactions.html',
                           transactionHistory=transactionsToDisplay)


@app.route('/deposits', methods=["GET", "POST"])
@login_required
def modifyDeposits():
    if request.method == "POST":
        depositAmount = float(request.form.get('amount'))
        transactionDate = request.form.get('date')
        percentToSavings = float(request.form.get('savingPercent'))

        to_savings = depositAmount * (percentToSavings / 100)
        to_checking = depositAmount - to_savings

        # Update balances
        current_user.checkingBalance += to_checking
        current_user.savingBalance += to_savings

        newTransaction = Transactions(username=current_user.username,
                                      date=transactionDate,
                                      purpose="deposit",
                                      amount=depositAmount,
                                      savingPercent=percentToSavings)
        db.session.add(newTransaction)
        db.session.commit()
        return render_template('deposits.html',
                               statusMessage='Deposit Successful')
    return render_template('deposits.html')


@app.route('/expenses', methods=["GET", "POST"])
@login_required
def modifyExpenses():
    if request.method == "POST":
        amountToDeduct = float(request.form.get('amount'))
        date = request.form.get('date')
        category = request.form.get('categories')

        current_user.checkingBalance -= amountToDeduct

        newTransaction = Transactions(username=current_user.username,
                                      date=date,
                                      purpose="withdrawal",
                                      amount=amountToDeduct,
                                      category=category)
        db.session.add(newTransaction)
        db.session.commit()
        return render_template('expenses.html',
                               statusMessage='Expense Recorded')
    return render_template('expenses.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect('/')
        else:
            return render_template('login.html',
                                   status='Invalid username or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        newname = request.form.get('username')
        newpass = request.form.get('password')

        if not User.query.filter_by(username=newname).first():
            user = User(username=newname,
                        password_hash=generate_password_hash(newpass),
                        checkingBalance=0.0,
                        savingBalance=0.0)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('/')
        else:
            return render_template('register.html',
                                   status="Username already exists!")
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# -------------------------
# Login Manager Loader
# -------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------------
# Run Server + Init DB
# -------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Seed default user
        if not User.query.filter_by(username="test").first():
            user1 = User(username="test",
                         password_hash=generate_password_hash("password123"),
                         checkingBalance=4.00,
                         savingBalance=0.00)
            db.session.add(user1)
            db.session.commit()

        # Seed some transactions
        if not Transactions.query.filter_by(username="test").first():
            transaction1 = Transactions(username="test", date="1/31/2021",
                                        purpose="deposit", amount=10.00,
                                        savingPercent=0.0)
            transaction2 = Transactions(username="test", date="2/10/2021",
                                        purpose="deposit", amount=10.00,
                                        savingPercent=0.0)
            db.session.add_all([transaction1, transaction2])
            db.session.commit()

    app.run(host='127.0.0.1', port=5000, debug=True)
