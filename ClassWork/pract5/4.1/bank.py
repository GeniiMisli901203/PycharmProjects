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
