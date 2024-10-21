import datetime
from typing import List, Dict
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class Transaction:
    def __init__(self, amount: float, transaction_type: str, description: str = ""):
        self.amount = amount
        self.type = transaction_type
        self.description = description
        self.date = datetime.datetime.now()

    def __str__(self):
        if self.description:
            return f"{self.date.strftime('%Y-%m-%d %H:%M:%S')} - {self.type}: {self.amount:.2f}€ - {self.description}"
        return f"{self.date.strftime('%Y-%m-%d %H:%M:%S')} - {self.type}: {self.amount:.2f}€"

class Account:
    def __init__(self, name: str, initial_balance: float, interest_rate: float, pin: str):
        self.name = name
        self.balance = initial_balance
        self.interest_rate = interest_rate
        self.pin = pin
        self.transactions: List[Transaction] = []
        self.last_interest_date = datetime.date.today().replace(day=1)

    def deposit(self, amount: float, description: str = ""):
        self.balance += amount
        self.transactions.append(Transaction(amount, "Dépôt", description))

    def withdraw(self, amount: float, description: str = "") -> bool:
        if self.balance >= amount:
            self.balance -= amount
            self.transactions.append(Transaction(amount, "Retrait", description))
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

    def transfer(self, from_account: Account, to_account_name: str, amount: float) -> bool:
        to_account = self.accounts.get(to_account_name)
        if to_account:
            if from_account.withdraw(amount, f"Transfert vers {to_account_name}"):
                to_account.deposit(amount, f"Transfert de {from_account.name}")
                return True
        return False

    def apply_monthly_interest_all_accounts(self):
        for account in self.accounts.values():
            account.apply_monthly_interest()

class BankGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Gestionnaire de Banque")
        self.bank = Bank()
        self.current_account = None

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill='both')

        self.main_frame = ttk.Frame(self.notebook)
        self.account_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.main_frame, text='Menu Principal')
        self.notebook.add(self.account_frame, text='Gestion de Compte')
        self.notebook.tab(1, state='disabled')

        # Main Frame
        ttk.Button(self.main_frame, text="Créer un compte", command=self.create_account).pack(pady=10)
        ttk.Button(self.main_frame, text="Accéder à un compte", command=self.access_account).pack(pady=10)
        ttk.Button(self.main_frame, text="Afficher tous les comptes", command=self.display_all_accounts).pack(pady=10)
        ttk.Button(self.main_frame, text="Quitter", command=self.master.quit).pack(pady=10)

        # Account Frame
        self.welcome_label = ttk.Label(self.account_frame, text="", font=("Arial", 14, "bold"))
        self.welcome_label.pack(pady=10)
        self.balance_label = ttk.Label(self.account_frame, text="")
        self.balance_label.pack(pady=10)

        ttk.Button(self.account_frame, text="Déposer", command=self.deposit).pack(pady=5)
        ttk.Button(self.account_frame, text="Retirer", command=self.withdraw).pack(pady=5)
        ttk.Button(self.account_frame, text="Afficher l'historique", command=self.display_history).pack(pady=5)
        ttk.Button(self.account_frame, text="Transférer", command=self.transfer).pack(pady=5)
        ttk.Button(self.account_frame, text="Retour au menu principal", command=self.back_to_main).pack(pady=5)

    def create_account(self):
        name = simpledialog.askstring("Nouveau compte", "Nom du compte:")
        if name:
            initial_balance = simpledialog.askfloat("Nouveau compte", "Solde initial:")
            interest_rate = simpledialog.askfloat("Nouveau compte", "Taux d'intérêt (en décimal, ex: 0.01 pour 1%):")
            pin = self.ask_pin("Nouveau compte", "Code PIN:")
            
            if self.bank.create_account(name, initial_balance, interest_rate, pin):
                messagebox.showinfo("Succès", f"Compte '{name}' créé avec succès.")
            else:
                messagebox.showerror("Erreur", f"Un compte avec le nom '{name}' existe déjà.")

    def access_account(self):
        name = simpledialog.askstring("Accès compte", "Nom du compte:")
        if name:
            pin = self.ask_pin("Accès compte", "Code PIN:")
            account = self.bank.get_account(name, pin)
            if account:
                self.current_account = account
                self.update_welcome_label()
                self.update_balance_label()
                self.notebook.tab(1, state='normal')
                self.notebook.select(self.account_frame)
            else:
                messagebox.showerror("Erreur", "Compte non trouvé ou PIN incorrect.")

    def display_all_accounts(self):
        accounts_info = "\n".join(str(account) for account in self.bank.accounts.values())
        messagebox.showinfo("Tous les comptes", accounts_info)

    def deposit(self):
        amount = simpledialog.askfloat("Dépôt", "Montant à déposer:")
        if amount:
            self.current_account.deposit(amount)
            self.update_balance_label()
            messagebox.showinfo("Succès", f"Dépôt de {amount:.2f}€ effectué.")

    def withdraw(self):
        amount = simpledialog.askfloat("Retrait", "Montant à retirer:")
        if amount:
            if self.current_account.withdraw(amount):
                self.update_balance_label()
                messagebox.showinfo("Succès", f"Retrait de {amount:.2f}€ effectué.")
            else:
                messagebox.showerror("Erreur", "Solde insuffisant.")

    def display_history(self):
        history = "\n".join(str(transaction) for transaction in self.current_account.get_transactions())
        messagebox.showinfo("Historique des transactions", history)

    def transfer(self):
        to_account_name = simpledialog.askstring("Transfert", "Nom du compte destinataire:")
        if to_account_name:
            amount = simpledialog.askfloat("Transfert", "Montant à transférer:")
            if amount:
                pin = self.ask_pin("Transfert", "Veuillez entrer votre code PIN pour confirmer le transfert:")
                if pin == self.current_account.pin:
                    if self.bank.transfer(self.current_account, to_account_name, amount):
                        self.update_balance_label()
                        messagebox.showinfo("Succès", f"Transfert de {amount:.2f}€ effectué vers {to_account_name}.")
                    else:
                        messagebox.showerror("Erreur", "Transfert échoué. Vérifiez le solde du compte ou le nom du destinataire.")
                else:
                    messagebox.showerror("Erreur", "Code PIN incorrect. Transfert annulé.")

    def back_to_main(self):
        self.current_account = None
        self.notebook.tab(1, state='disabled')
        self.notebook.select(self.main_frame)

    def update_welcome_label(self):
        if self.current_account:
            self.welcome_label.config(text=f"Bienvenue, {self.current_account.name}!")

    def update_balance_label(self):
        if self.current_account:
            self.balance_label.config(text=f"Solde actuel : {self.current_account.get_balance():.2f}€")

    def ask_pin(self, title, prompt):
        def on_ok():
            nonlocal pin
            pin = entry.get()
            dialog.destroy()

        pin = None
        dialog = tk.Toplevel(self.master)
        dialog.title(title)
        ttk.Label(dialog, text=prompt).pack(pady=5)
        entry = ttk.Entry(dialog, show="*")
        entry.pack(pady=5)
        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        dialog.grab_set()
        self.master.wait_window(dialog)
        return pin

    def run(self):
        self.master.mainloop()

root = tk.Tk()
app = BankGUI(root)
app.run()