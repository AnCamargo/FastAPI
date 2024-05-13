import pytest

def add(x:int, y:int):
    return x+y

class InsufficientFunds(Exception):
    pass

class BankAccount():
    def __init__(self, starting_balance=0):
        self.balance = starting_balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFunds("Insufficient funds in account")
        self.balance -= amount

    def collect_interest(self, amount):
        self.balance *= 1.1

@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def bank_account():
    return BankAccount(50)

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
def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 50

def test_bank_default_initial_amount(zero_bank_account):
    #bank_account = BankAccount()
    assert zero_bank_account.balance == 0

def test_bank_withdraw_amount(bank_account):
    bank_account.withdraw(20)
    assert bank_account.balance == 30

@pytest.mark.parametrize("deposited, withdraw, expected",[
    (200,100,100),
    (50,10,40),
    (1200,200,1000)
])
def test_bank_transaction(zero_bank_account, deposited, withdraw, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdraw)
    assert zero_bank_account.balance == expected

def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(200)
