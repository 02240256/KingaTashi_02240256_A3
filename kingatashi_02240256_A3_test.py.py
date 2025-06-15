import unittest
from BankingApplication import Account, PersonalAccount, BusinessAccount, BankingSystem

class TestBankingSystem(unittest.TestCase):
    
    def setUp(self):
        # Initialize test accounts and a mock banking system before each test
        self.acc1 = PersonalAccount("12345", "0000", 100.0)  # Personal account with initial balance
        self.acc2 = BusinessAccount("67890", "1111", 50.0)   # Business account with initial balance
        self.bank = BankingSystem(filename="test_accounts.txt")  # Use a test file to avoid overwriting real data
        self.bank.accounts = {
            "12345": self.acc1,
            "67890": self.acc2
        }

    # --------- 1. Tests for invalid or unusual user input ---------

    def test_deposit_negative_amount(self):
        # Depositing a negative amount should raise an error
        with self.assertRaises(ValueError):
            self.acc1.deposit(-100)

    def test_withdraw_negative_amount(self):
        # Withdrawing a negative amount should raise an error
        with self.assertRaises(ValueError):
            self.acc1.withdraw(-50)

    def test_recharge_invalid_number(self):
        # Attempt to recharge using an invalid phone number format
        with self.assertRaises(ValueError):
            self.acc1.recharge(10, "123456")  # Invalid: too short and wrong prefix

    def test_recharge_valid_number(self):
        # Successfully recharge a valid mobile number
        result = self.acc1.recharge(10, "77123456")
        self.assertIn("Topped up Nu10.00 to 77123456", result)

    # --------- 2. Tests for invalid operations or edge cases ---------

    def test_withdraw_insufficient_funds(self):
        # Attempt to withdraw more than available balance should raise an error
        with self.assertRaises(ValueError):
            self.acc2.withdraw(1000)

    def test_transfer_to_invalid_account(self):
        # Transferring to a non-existent (None) account should raise an error
        with self.assertRaises(ValueError):
            self.acc1.transfer(10, None)

    def test_transfer_insufficient_funds(self):
        # Transfer more than the sender's balance should raise an error
        with self.assertRaises(ValueError):
            self.acc2.transfer(1000, self.acc1)

    # --------- 3. Tests for normal/valid operations ---------

    def test_deposit_function(self):
        # Verify deposit increases balance correctly
        balance_before = self.acc1.funds
        msg = self.acc1.deposit(50)
        self.assertEqual(self.acc1.funds, balance_before + 50)
        self.assertIn("Deposited", msg)

    def test_withdraw_function(self):
        # Verify withdrawal reduces balance correctly
        balance_before = self.acc1.funds
        msg = self.acc1.withdraw(40)
        self.assertEqual(self.acc1.funds, balance_before - 40)
        self.assertIn("Withdrew", msg)

    def test_transfer_function(self):
        # Transfer funds from one account to another and validate balances
        self.acc1.funds = 100
        self.acc2.funds = 50
        msg = self.acc1.transfer(25, self.acc2)
        self.assertEqual(self.acc1.funds, 75)
        self.assertEqual(self.acc2.funds, 75)
        self.assertIn("Transferred", msg)

    def test_delete_account_function(self):
        # Delete an account and confirm it is removed from the system
        self.bank.delete_account("12345")
        self.assertNotIn("12345", self.bank.accounts)

    def test_login_success(self):
        # Successful login with correct credentials
        acc = self.bank.login("12345", "0000")
        self.assertEqual(acc.account_id, "12345")

    def test_login_fail(self):
        # Failed login with incorrect passcode should raise an error
        with self.assertRaises(ValueError):
            self.bank.login("12345", "wrong")

# Run the tests when the script is executed
if __name__ == '__main__':
    unittest.main()
