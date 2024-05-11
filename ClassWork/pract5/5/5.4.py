import sqlite3
import hypothesis.strategies as st
import hypothesis

def create_account(account_number, balance):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS accounts (account_number INTEGER PRIMARY KEY, balance REAL)")
    cursor.execute(
        "INSERT INTO accounts (account_number, balance) VALUES (?, ?)", (account_number, balance))
    conn.commit()
    conn.close()

def get_balance(account_number):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT balance FROM accounts WHERE account_number = ?", (account_number,))
    balance = cursor.fetchone()[0]
    conn.close()
    return balance

def deposit(account_number, amount):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE accounts SET balance = balance + ? WHERE account_number = ?", (amount, account_number))
    conn.commit()
    conn.close()

def withdraw(account_number, amount):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT balance FROM accounts WHERE account_number = ?", (account_number,))
    balance = cursor.fetchone()[0]
    if balance >= amount:
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE account_number = ?", (amount, account_number))
        conn.commit()
    conn.close()
@hypothesis.given(st.integers(min_value=1), st.floats(min_value=0))
def test_bank_account_model(account_number, initial_balance):
    create_account(account_number, initial_balance)
    model = {initial_balance: {}}
    for _ in range(10):
        current_balance = hypothesis.example().draw(st.sampled_from(list(model.keys())))
        action = hypothesis.example().draw(st.sampled_from(["deposit", "withdraw"]))
        if action == "deposit":
            amount = hypothesis.example().draw(st.floats(min_value=0))
            deposit(account_number, amount)
            new_balance = get_balance(account_number)
            if new_balance not in model:
                model[new_balance] = {}
            model[current_balance][action] = new_balance
        elif action == "withdraw":
            amount = hypothesis.example().draw(st.floats(min_value=0, max_value=current_balance))
            withdraw(account_number, amount)
            new_balance = get_balance(account_number)
            if new_balance not in model:
                model[new_balance] = {}
            model[current_balance][action] = new_balance
if __name__ == "__main__":
    hypothesis.main()
