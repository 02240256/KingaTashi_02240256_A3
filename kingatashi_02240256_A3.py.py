import random
import tkinter as tk
from tkinter import messagebox, simpledialog

# -------------------- Account Base Class --------------------

class Account:
    def __init__(self, account_id, passcode, funds=0.0):
        self.account_id = account_id
        self.passcode = passcode
        self.funds = funds
        self.account_category = "Generic"

    # Add funds to the account
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.funds += amount
        return f"Deposited Nu{amount:.2f}. New balance: Nu{self.funds:.2f}"

    # Withdraw funds from the account
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.funds < amount:
            raise ValueError("Insufficient funds.")
        self.funds -= amount
        return f"Withdrew Nu{amount:.2f}. New balance: Nu{self.funds:.2f}"

    # Transfer funds to another account
    def transfer(self, amount, recipient_account):
        if recipient_account is None:
            raise ValueError("Recipient account not found.")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        if self.funds < amount:
            raise ValueError("Insufficient funds.")
        self.withdraw(amount)
        recipient_account.deposit(amount)
        return f"Transferred Nu{amount:.2f} to {recipient_account.account_id}"
    
    # Mobile recharge (only for valid Bhutanese numbers starting with 77 or 17)
    def recharge(self, amount, phone_number):
        prefix = phone_number[:2]
        if len(phone_number) == 8 and prefix in ("77", "17"):
            self.withdraw(amount)
            return f"Topped up Nu{amount:.2f} to {phone_number}. Remaining balance: Nu{self.funds:.2f}"
        else:
            raise ValueError("Invalid phone number. Must be 8 digits and start with 77 or 17.")

# -------------------- Derived Account Types --------------------

class PersonalAccount(Account):
    def __init__(self, account_id, passcode, funds=0.0):
        super().__init__(account_id, passcode, funds)
        self.account_category = "Personal"

class BusinessAccount(Account):
    def __init__(self, account_id, passcode, funds=0.0):
        super().__init__(account_id, passcode, funds)
        self.account_category = "Business"

# -------------------- Core Banking Logic --------------------

class BankingSystem:
    def __init__(self, filename="accounts.txt"):
        self.filename = filename
        self.accounts = self.load_accounts()  # Load accounts from file at startup

    # Load account data from file
    def load_accounts(self):
        accounts = {}
        try:
            with open(self.filename, "r") as file:
                for line in file:
                    account_id, passcode, category, funds = line.strip().split(",")
                    funds = float(funds)
                    if category == "Personal":
                        account = PersonalAccount(account_id, passcode, funds)
                    else:
                        account = BusinessAccount(account_id, passcode, funds)
                    accounts[account_id] = account
        except FileNotFoundError:
            pass  # If no file, return empty account list
        return accounts

    # Save current account data to file
    def save_accounts(self):
        with open(self.filename, "w") as file:
            for account in self.accounts.values():
                file.write(f"{account.account_id},{account.passcode},{account.account_category},{account.funds}\n")

    # Create a new account (random ID and passcode)
    def create_account(self, account_type):
        account_id = str(random.randint(10000, 99999))
        while account_id in self.accounts:  # Ensure uniqueness
            account_id = str(random.randint(10000, 99999))
        passcode = str(random.randint(1000, 9999))
        if account_type == "Personal":
            account = PersonalAccount(account_id, passcode)
        else:
            account = BusinessAccount(account_id, passcode)
        self.accounts[account_id] = account
        self.save_accounts()
        return account

    # Validate login credentials
    def login(self, account_id, passcode):
        account = self.accounts.get(account_id)
        if account and account.passcode == passcode:
            return account
        raise ValueError("Account ID or passcode is incorrect.")

    # Delete an account
    def delete_account(self, account_id):
        if account_id in self.accounts:
            del self.accounts[account_id]
            self.save_accounts()
        else:
            raise ValueError("Account not found.")

# -------------------- GUI Application --------------------

class BankingGUI:
    def __init__(self, root, bank_system):
        self.root = root
        self.bank = bank_system
        self.account = None  # Currently logged-in account
        root.title("Banking System")

        # Login/Create Account Frame
        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        self.status_label = tk.Label(self.frame, text="Please login or create an account")
        self.status_label.grid(row=0, column=0, columnspan=2)

        tk.Label(self.frame, text="Account ID").grid(row=1, column=0)
        self.id_entry = tk.Entry(self.frame)
        self.id_entry.grid(row=1, column=1)

        tk.Label(self.frame, text="Passcode").grid(row=2, column=0)
        self.pass_entry = tk.Entry(self.frame, show="*")
        self.pass_entry.grid(row=2, column=1)

        self.login_btn = tk.Button(self.frame, text="Login", command=self.login)
        self.login_btn.grid(row=3, column=0, pady=5)

        self.create_btn = tk.Button(self.frame, text="Create Account", command=self.create_account)
        self.create_btn.grid(row=3, column=1)

        # Actions Frame (after login)
        self.actions_frame = tk.Frame(root)
        self.actions_frame.pack(padx=10, pady=10)

        # Buttons for all banking actions
        tk.Button(self.actions_frame, text="Check Balance", command=self.check_balance).pack(fill="x")
        tk.Button(self.actions_frame, text="Deposit", command=self.deposit).pack(fill="x")
        tk.Button(self.actions_frame, text="Withdraw", command=self.withdraw).pack(fill="x")
        tk.Button(self.actions_frame, text="Transfer", command=self.transfer).pack(fill="x")
        tk.Button(self.actions_frame, text="Recharge", command=self.recharge).pack(fill="x")
        tk.Button(self.actions_frame, text="Delete Account", command=self.delete_account).pack(fill="x")

    # -------------------- GUI Functionality --------------------

    def login(self):
        aid = self.id_entry.get()
        pwd = self.pass_entry.get()
        try:
            self.account = self.bank.login(aid, pwd)
            self.status_label.config(text=f"Logged in as {self.account.account_id} ({self.account.account_category})")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_account(self):
        acc_type = messagebox.askquestion("Account Type", "Do you want a Personal account? (No = Business)")
        account = self.bank.create_account("Personal" if acc_type == 'yes' else "Business")
        messagebox.showinfo("Account Created", f"ID: {account.account_id}\nPasscode: {account.passcode}")

    def check_balance(self):
        if self.account:
            messagebox.showinfo("Balance", f"Current balance: Nu{self.account.funds:.2f}")

    def deposit(self):
        if self.account:
            try:
                amount = float(simpledialog.askstring("Deposit", "Enter amount to deposit:"))
                msg = self.account.deposit(amount)
                self.bank.save_accounts()
                messagebox.showinfo("Success", msg)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def withdraw(self):
        if self.account:
            try:
                amount = float(simpledialog.askstring("Withdraw", "Enter amount to withdraw:"))
                msg = self.account.withdraw(amount)
                self.bank.save_accounts()
                messagebox.showinfo("Success", msg)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def transfer(self):
        if self.account:
            try:
                recipient_id = simpledialog.askstring("Transfer", "Enter recipient Account ID:")
                amount = float(simpledialog.askstring("Transfer", "Enter amount to transfer:"))
                recipient = self.bank.accounts[recipient_id]
                msg = self.account.transfer(amount, recipient)
                self.bank.save_accounts()
                messagebox.showinfo("Success", msg)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def recharge(self):
        if self.account:
            try:
                phone = simpledialog.askstring("Recharge", "Enter phone number:")
                amount = float(simpledialog.askstring("Recharge", "Enter amount to recharge:"))
                msg = self.account.recharge(amount, phone)
                self.bank.save_accounts()
                messagebox.showinfo("Success", msg)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_account(self):
        if self.account:
            try:
                confirm = messagebox.askyesno("Delete Account", "Are you sure you want to delete your account?")
                if confirm:
                    self.bank.delete_account(self.account.account_id)
                    messagebox.showinfo("Deleted", "Account deleted successfully.")
                    self.account = None
                    self.status_label.config(text="Please login or create an account")
            except Exception as e:
                messagebox.showerror("Error", str(e))

# -------------------- Run GUI App --------------------

if __name__ == "__main__":
    system = BankingSystem()
    root = tk.Tk()
    gui = BankingGUI(root, system)
    root.mainloop()