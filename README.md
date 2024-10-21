
# 🏦 Application Bancaire Simplifiée avec Flask

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
app.config['SECRET_KEY'] = '[VOTRE_API_KEY]'
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


## ✨ But du projet : Version adaptée avec Flask

Ce projet est une adaptation Flask d'un gestionnaire de comptes bancaires simplifié, basé sur l'énoncé fourni. L'objectif est de permettre aux utilisateurs de gérer leurs comptes bancaires à travers une interface web plutôt qu'une application en ligne de commande. Grâce à Flask et SQLAlchemy, nous avons transformé la logique d'une application Python basique en un système complet, doté de fonctionnalités telles que la création de comptes, la gestion des transactions et la sécurité des comptes par code PIN.

### 🚀 Fonctionnalités réalisées par rapport à l'énoncé

1. **👤 Création d'un compte :**
   - L'application permet à un utilisateur de créer un compte bancaire avec un nom, un solde initial, un taux d'intérêt et un code PIN. Cette fonctionnalité est gérée par la route `/create_account`, qui stocke le compte dans la base de données SQL pour une **persistance des données**.

2. **💰 Consultation du solde :**
   - L'utilisateur peut consulter son solde après s'être connecté via la route `/account`, où le solde actuel de son compte s'affiche, ainsi que les informations sur les taux d'intérêt.

3. **📥 Dépôt d'argent :**
   - Grâce à la route `/deposit`, l'utilisateur peut déposer de l'argent sur son compte, en ajoutant le montant au solde actuel. Les transactions sont enregistrées dans la base de données pour être consultées ultérieurement.

4. **📤 Retrait d'argent :**
   - L'utilisateur peut retirer de l'argent via la route `/withdraw`, tant que le montant est disponible sur le compte. Le solde ne peut pas devenir négatif.

5. **📝 Historique des transactions :**
   - Toutes les transactions (dépôts, retraits, transferts) sont enregistrées dans une table `Transaction`, et l'historique peut être consulté via la route `/history`. Cette historique est sauvegardée dans la base de données pour être récupérée à tout moment.

6. **🔄 Menu d'options (adapté pour le web) :**
   - Au lieu d'un menu d'options en ligne de commande, les fonctionnalités sont organisées sous forme de pages et formulaires accessibles via différentes routes : création de compte, dépôt, retrait, transfert, etc.

7. **📈 Ajout d'intérêts mensuels :**
   - Un calcul automatique des intérêts mensuels est appliqué à chaque compte via la méthode `apply_monthly_interest`, qui est déclenchée pour tous les comptes lors de l'exécution de la fonction `apply_monthly_interest_all_accounts`.

8. **🏦 Possibilité de créer plusieurs comptes :**
   - L'application supporte la création de plusieurs comptes par utilisateur. Chaque compte est associé à un nom unique et possède un solde, un taux d'intérêt et un code PIN. L'utilisateur peut gérer plusieurs comptes en se connectant via la route `/login`.

9. **💸 Transfert d'argent entre comptes :**
   - La fonctionnalité de transfert est présente via la route `/transfer`. L'utilisateur peut transférer de l'argent entre ses comptes en spécifiant un compte de destination, avec une validation par code PIN. Les transferts sont enregistrés dans la base de données pour la persistance.

10. **🔍 Affichage des détails des comptes :**
    - Les détails de chaque compte (solde, taux d'intérêt, historique des transactions) sont affichés sur la page `/account` une fois l'utilisateur connecté.

11. **🔐 Sécurité avec code PIN :**
    - Chaque compte est protégé par un code PIN que l'utilisateur doit saisir pour accéder à ses comptes. Lors de l'authentification via la route `/login`, le code PIN est vérifié pour permettre ou refuser l'accès.

### 📈 Points d'amélioration possibles
- **⚠️ Meilleure gestion des erreurs :** Une meilleure gestion des erreurs pourrait être ajoutée pour gérer les cas spécifiques comme les erreurs de connexion, les transferts invalides, etc.
- **🔒 Sécurité accrue :** Actuellement, les PINs sont stockés en texte clair, ce qui pourrait être amélioré en les hachant avant de les stocker dans la base de données.
- **⏲️ Automatisation des intérêts :** L'ajout automatique des intérêts pourrait être planifié pour s'exécuter à des intervalles réguliers sans nécessiter d'intervention manuelle.
  
En conclusion, cette version Flask de l'application "Gestionnaire de Banque Simplifié" adapte les fonctionnalités de l'énoncé pour les intégrer dans une interface web moderne et interactive, tout en maintenant les mêmes concepts de base liés à la gestion des comptes, des transactions, et de la sécurité. La persistance des données est assurée grâce à une base de données SQL.
