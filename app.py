import datetime
from typing import List, Dict
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '6a5955391897583ef1563b15bbe86fdf42a9b94d2d384e1c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banque.db'
db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))
    is_incoming = db.Column(db.Boolean, default=True)  # Nouveau champ
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    def __str__(self):
        direction = "reçu" if self.is_incoming else "envoyé"
        desc = f" - {self.description}" if self.description else ""
        return f"{self.date.strftime('%Y-%m-%d %H:%M:%S')} - {self.transaction_type} {direction}: {self.amount:.2f}€{desc}"

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0)
    interest_rate = db.Column(db.Float, nullable=False)
    pin = db.Column(db.String(4), nullable=False)
    last_interest_date = db.Column(db.Date, default=datetime.date.today().replace(day=1))
    transactions = db.relationship('Transaction', backref='account', lazy=True)

    def deposit(self, amount: float, description: str = ""):
        self.balance += amount
        new_transaction = Transaction(amount=amount, transaction_type="Dépôt", description=description, account=self)
        db.session.add(new_transaction)
        db.session.commit()

    def withdraw(self, amount: float, description: str = "") -> bool:
        if self.balance >= amount:
            self.balance -= amount
            new_transaction = Transaction(amount=amount, transaction_type="Retrait", description=description, account=self)
            db.session.add(new_transaction)
            db.session.commit()
            return True
        return False

    def get_balance(self) -> float:
        return self.balance

    def get_transactions(self) -> List[Transaction]:
        return self.transactions

    def apply_monthly_interest(self):
        today = datetime.date.today()
        if today.month != self.last_interest_date.month or today.year != self.last_interest_date.year:
            interest = self.balance * (self.interest_rate / 12)
            self.balance += interest
            new_transaction = Transaction(amount=interest, transaction_type="Intérêts", account=self)
            db.session.add(new_transaction)
            self.last_interest_date = today
            db.session.commit()

    def __str__(self):
        return f"Compte {self.name}: Solde = {self.balance:.2f}€, Taux d'intérêt = {self.interest_rate*100:.2f}%"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        name = request.form['name']
        initial_balance = float(request.form['initial_balance'])
        interest_rate = float(request.form['interest_rate'])
        pin = request.form['pin']

        existing_account = Account.query.filter_by(name=name).first()
        if existing_account:
            flash(f"Un compte avec le nom '{name}' existe déjà.", 'error')
        else:
            new_account = Account(name=name, balance=initial_balance, interest_rate=interest_rate, pin=pin)
            db.session.add(new_account)
            db.session.commit()
            flash(f"Compte '{name}' créé avec succès.", 'success')
            return redirect(url_for('home'))

    return render_template('create_account.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        pin = request.form['pin']
        account = Account.query.filter_by(name=name, pin=pin).first()
        if account:
            session['account_id'] = account.id
            flash(f"Bienvenue, {account.name}!", 'success')
            return redirect(url_for('account'))
        else:
            flash("Compte non trouvé ou PIN incorrect.", 'error')
    return render_template('login.html')

@app.route('/account')
def account():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    account = Account.query.get(session['account_id'])
    return render_template('account.html', account=account)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    account = Account.query.get(session['account_id'])
    if request.method == 'POST':
        amount = float(request.form['amount'])
        account.deposit(amount)
        flash(f"Dépôt de {amount:.2f}€ effectué.", 'success')
        return redirect(url_for('account'))
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    account = Account.query.get(session['account_id'])
    if request.method == 'POST':
        amount = float(request.form['amount'])
        if account.withdraw(amount):
            flash(f"Retrait de {amount:.2f}€ effectué.", 'success')
        else:
            flash("Solde insuffisant.", 'error')
        return redirect(url_for('account'))
    return render_template('withdraw.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    account = Account.query.get(session['account_id'])
    if request.method == 'POST':
        to_account_name = request.form['to_account_name']
        amount = float(request.form['amount'])
        pin = request.form['pin']
        
        if account.pin != pin:
            flash("Code PIN incorrect. Transfert annulé.", 'error')
            return redirect(url_for('account'))
        
        to_account = Account.query.filter_by(name=to_account_name).first()
        if to_account:
            if account.balance >= amount:
                # Transaction sortante pour le compte émetteur
                outgoing_transaction = Transaction(
                    amount=amount,
                    transaction_type="Transfert",
                    description=f"vers {to_account_name}",
                    is_incoming=False,
                    account=account
                )
                account.balance -= amount
                
                # Transaction entrante pour le compte destinataire
                incoming_transaction = Transaction(
                    amount=amount,
                    transaction_type="Transfert",
                    description=f"de {account.name}",
                    is_incoming=True,
                    account=to_account
                )
                to_account.balance += amount
                
                db.session.add(outgoing_transaction)
                db.session.add(incoming_transaction)
                db.session.commit()
                
                flash(f"Transfert de {amount:.2f}€ effectué vers {to_account_name}.", 'success')
            else:
                flash("Transfert échoué. Solde insuffisant.", 'error')
        else:
            flash("Compte destinataire non trouvé.", 'error')
        return redirect(url_for('account'))
    return render_template('transfer.html')

@app.route('/history')
def history():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    account = Account.query.get(session['account_id'])
    transactions = account.get_transactions()
    return render_template('history.html', transactions=transactions)

@app.route('/logout')
def logout():
    session.pop('account_id', None)
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('home'))

def apply_monthly_interest_all_accounts():
    accounts = Account.query.all()
    for account in accounts:
        account.apply_monthly_interest()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)