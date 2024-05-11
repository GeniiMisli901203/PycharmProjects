import pytest
from bank_account import BankAccount

def test_deposit():
    account = BankAccount(12345)
    account.deposit(100)
    assert account.balance == 100

def test_withdraw():
    account = BankAccount(12345)
    account.deposit(200)
    account.withdraw(100)
    assert account.balance == 100

def test_withdraw_insufficient_funds():
    account = BankAccount(12345)
    account.deposit(100)

    with pytest.raises(ValueError, match="Insufficient funds in the account"):
        account.withdraw(200)

def test_check_balance():
    account = BankAccount(12345)
    account.deposit(300)
    assert account.check_balance() == "Balance on account 12345: 300"
