import datetime
from typing import List, Dict

class Transaction:
    def __init__(self, amount: float, transaction_type: str):
        self.amount = amount
        self.type = transaction_type
        self.date = datetime.datetime.now()

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d %H:%M:%S')} - {self.type}: {self.amount:.2f}€"

class Account:
    def __init__(self, name: str, initial_balance: float, interest_rate: float, pin: str):
        self.name = name
        self.balance = initial_balance
        self.interest_rate = interest_rate
        self.pin = pin
        self.transactions: List[Transaction] = []
        self.last_interest_date = datetime.date.today().replace(day=1)

    def deposit(self, amount: float):
        self.balance += amount
        self.transactions.append(Transaction(amount, "Dépôt"))

    def withdraw(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            self.transactions.append(Transaction(amount, "Retrait"))
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
            self.transactions.append(Transaction(interest, "Intérêts"))
            self.last_interest_date = today

    def __str__(self):
        return f"Compte {self.name}: Solde = {self.balance:.2f}€, Taux d'intérêt = {self.interest_rate*100:.2f}%"

class Bank:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    def create_account(self, name: str, initial_balance: float, interest_rate: float, pin: str) -> bool:
        if name not in self.accounts:
            self.accounts[name] = Account(name, initial_balance, interest_rate, pin)
            return True
        return False

    def get_account(self, name: str, pin: str) -> Account:
        account = self.accounts.get(name)
        if account and account.pin == pin:
            return account
        return None

    def transfer(self, from_account: Account, to_account: Account, amount: float) -> bool:
        if from_account.withdraw(amount):
            to_account.deposit(amount)
            return True
        return False

    def apply_monthly_interest_all_accounts(self):
        for account in self.accounts.values():
            account.apply_monthly_interest()

def main():
    bank = Bank()

    while True:
        print("\n1. Créer un compte")
        print("2. Accéder à un compte")
        print("3. Afficher tous les comptes")
        print("4. Quitter")

        choice = input("Choisissez une option : ")

        if choice == "1":
            name = input("Nom du compte : ")
            initial_balance = float(input("Solde initial : "))
            interest_rate = float(input("Taux d'intérêt (en décimal, ex: 0.01 pour 1%) : "))
            pin = input("Code PIN : ")

            if bank.create_account(name, initial_balance, interest_rate, pin):
                print(f"Compte '{name}' créé avec succès.")
            else:
                print(f"Un compte avec le nom '{name}' existe déjà.")

        elif choice == "2":
            name = input("Nom du compte : ")
            pin = input("Code PIN : ")
            account = bank.get_account(name, pin)

            if account:
                while True:
                    print(f"\nCompte : {account.name}")
                    print("1. Consulter le solde")
                    print("2. Déposer de l'argent")
                    print("3. Retirer de l'argent")
                    print("4. Afficher l'historique des transactions")
                    print("5. Transférer de l'argent")
                    print("6. Retour au menu principal")

                    sub_choice = input("Choisissez une option : ")

                    if sub_choice == "1":
                        print(f"Solde actuel : {account.get_balance():.2f}€")
                    elif sub_choice == "2":
                        amount = float(input("Montant à déposer : "))
                        account.deposit(amount)
                        print(f"Dépôt de {amount:.2f}€ effectué.")
                    elif sub_choice == "3":
                        amount = float(input("Montant à retirer : "))
                        if account.withdraw(amount):
                            print(f"Retrait de {amount:.2f}€ effectué.")
                        else:
                            print("Solde insuffisant.")
                    elif sub_choice == "4":
                        print("Historique des transactions :")
                        for transaction in account.get_transactions():
                            print(transaction)
                    elif sub_choice == "5":
                        to_account_name = input("Nom du compte destinataire : ")
                        to_account_pin = input("Code PIN du compte destinataire : ")
                        to_account = bank.get_account(to_account_name, to_account_pin)
                        if to_account:
                            amount = float(input("Montant à transférer : "))
                            if bank.transfer(account, to_account, amount):
                                print(f"Transfert de {amount:.2f}€ effectué.")
                            else:
                                print("Transfert échoué. Vérifiez le solde du compte source.")
                        else:
                            print("Compte destinataire non trouvé ou PIN incorrect.")
                    elif sub_choice == "6":
                        break
            else:
                print("Compte non trouvé ou PIN incorrect.")

        elif choice == "3":
            print("Liste des comptes :")
            for account in bank.accounts.values():
                print(account)

        elif choice == "4":
            print("Merci d'avoir utilisé notre service bancaire. Au revoir !")
            break

        bank.apply_monthly_interest_all_accounts()

main()