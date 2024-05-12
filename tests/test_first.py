import pytest

def add(x:int, y:int):
    return x+y

class BankAccount():
    def __init__(self, starting_balance=0):
        self.balance = starting_balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        self.balance -= amount

    def collect_interest(self, amount):
        self.balance *= 1.1

@pytest.mark.parametrize("num1, num2, expected", [
    (1,2,3),
    (4,5,9),
    (10,11,21)
])
def test_add(num1, num2, expected):
    print("testing add function")
    assert add(num1,num2) == expected

# @pytest.mark.parametrize("balance1, expected", [
#     (0,0),
#     (50,50)
# ])
def test_bank_set_initial_amount():
    bank_account = BankAccount(50)
    assert bank_account.balance == 50

def test_bank_default_initial_amount():
    bank_account = BankAccount()
    assert bank_account.balance == 0

def test_bank_withdraw_amount():
    bank_account = BankAccount(50)
    bank_account.withdraw(20)
    assert bank_account.balance == 30