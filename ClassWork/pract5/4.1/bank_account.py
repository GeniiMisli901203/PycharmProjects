from deal import pre, post, ensure, raises, has

class BankAccount:
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance

    @pre(lambda self, amount: amount > 0)
    @post(lambda self, amount, result: self.balance == self.balance + amount)
    @ensure(lambda self, amount, result: self.balance >= amount)
    def deposit(self, amount):
        self.balance += amount
        return f"{amount} средств успешно зачислены на счет {self.account_number}"

    @pre(lambda self, amount: amount > 0 and amount <= self.balance)
    @post(lambda self, amount, result: self.balance == self.balance - amount)
    @raises(ValueError, reason="Недостаточно средств на счете")
    @ensure(lambda self, amount, result: self.balance >= 0)
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Недостаточно средств на счете")
        self.balance -= amount
        return f"{amount} средств успешно сняты с счета {self.account_number}"

    @has("balance")
    def check_balance(self):
        return f"Баланс счета {self.account_number}: {self.balance}"
