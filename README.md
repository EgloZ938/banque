
# 🏦 Application Bancaire Simplifiée avec Flask

## 📚 Table des matières
1. [Introduction](#introduction)
2. [Structure de l'application](#structure-de-lapplication)
3. [Fonctionnalités principales](#fonctionnalités-principales)
4. [Routes et logique métier](#routes-et-logique-métier)
5. [Gestion des sessions et sécurité](#gestion-des-sessions-et-sécurité)
6. [Gestion des erreurs et messages flash](#gestion-des-erreurs-et-messages-flash)
7. [Intérêts mensuels](#intérêts-mensuels)
8. [Point d'entrée de l'application](#point-dentrée-de-lapplication)
9. [Améliorations possibles et conclusion](#améliorations-possibles-et-conclusion)

## 🌟 Introduction

Cette application est un système bancaire simplifié, créé avec Python et le framework web Flask. Elle permet aux utilisateurs de gérer des comptes bancaires, effectuer des dépôts, des retraits et des transferts, ainsi que de consulter l'historique des transactions.

### 🛠️ Technologies utilisées :
- **Python** : Le langage de programmation principal
- **Flask** : Un micro-framework web pour Python
- **SQLAlchemy** : Une bibliothèque ORM pour gérer la base de données

## 🏗️ Structure de l'application

### Configuration de Flask et de la base de données

```python
app = Flask(__name__)
app.config['SECRET_KEY'] = '6a5955391897583ef1563b15bbe86fdf42a9b94d2d384e1c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banque.db'
db = SQLAlchemy(app)
```

Ces lignes initialisent l'application Flask et configurent la base de données SQLite.

### 📊 Modèles de données
Deux classes principales définissent la structure de nos données :

#### 💸 Classe Transaction
```python
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))
    is_incoming = db.Column(db.Boolean, default=True)  # Nouveau champ
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

    def __str__(self):
        direction = "reçu" si self.is_incoming sinon "envoyé"
        desc = f" - {self.description}" si self.description sinon ""
        return f"{self.date.strftime('%Y-%m-%d %H:%M:%S')} - {self.transaction_type} {direction}: {self.amount:.2f}€{desc}"
```

#### 🏦 Classe Account
```python
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0)
    interest_rate = db.Column(db.Float, nullable=False)
    pin = db.Column(db.String(4), nullable=False)
    last_interest_date = db.Column(db.Date, default=datetime.date.today().replace(day=1))
    transactions = db.relationship('Transaction', backref='account', lazy=True)
```

Les fonctions `deposit`, `withdraw` et `apply_monthly_interest` gèrent les transactions et les intérêts :

```python
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

def apply_monthly_interest(self):
    today = datetime.date.today()
    if today.month != self.last_interest_date.month or today.year != self.last_interest_date.year:
        interest = self.balance * (self.interest_rate / 12)
        self.balance += interest
        new_transaction = Transaction(amount=interest, transaction_type="Intérêts", account=self)
        db.session.add(new_transaction)
        self.last_interest_date = today
        db.session.commit()
```

## 🚪 Routes et logique métier

L'application comporte plusieurs routes pour gérer les comptes et les transactions :

### Route `/create_account`
Permet de créer un nouveau compte bancaire.

```python
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    # Code pour créer un compte
```

### Route `/login`
Gère la connexion des utilisateurs.

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Code pour gérer la connexion
```

### Route `/account`
Affiche le compte de l'utilisateur connecté.

```python
@app.route('/account')
def account():
    # Code pour afficher les détails du compte
```

## 🔐 Gestion des sessions et sécurité

Les sessions sont gérées par Flask pour maintenir l'état de connexion des utilisateurs :

```python
session['account_id'] = account.id
```

L'utilisateur est redirigé vers la page de connexion s'il n'est pas authentifié.

## 🚨 Gestion des erreurs et messages flash

Les messages flash sont utilisés pour informer l'utilisateur en cas d'erreurs ou de succès.

```python
flash("Message d'erreur ou de succès", 'success' ou 'error')
```

## 📈 Intérêts mensuels

Les intérêts sont appliqués mensuellement à tous les comptes :

```python
def apply_monthly_interest_all_accounts():
    accounts = Account.query.all()
    for account in accounts:
        account.apply_monthly_interest()
```

## 🚀 Point d'entrée de l'application

Le point d'entrée du code est la partie suivante :

```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

## 🔧 Améliorations possibles et conclusion

- Ajouter une meilleure gestion des erreurs
- Améliorer la sécurité des PINs (actuellement en texte clair)
- Ajouter des fonctionnalités avancées comme les virements automatiques
