import sqlite3
import hypothesis.strategies as st
import hypothesis
import bank
@hypothesis.given(st.integers(min_value=1), st.floats(min_value=0))
def test_bank_account_model(account_number, initial_balance):
    bank.create_account(account_number, initial_balance)
    model = {initial_balance: {}}
    for _ in range(10):
        current_balance = hypothesis.example().draw(st.sampled_from(list(model.keys())))
        action = hypothesis.example().draw(st.sampled_from(["deposit", "withdraw"]))
        if action == "deposit":
            amount = hypothesis.example().draw(st.floats(min_value=0))
            bank.deposit(account_number, amount)
            new_balance = bank.get_balance(account_number)
            if new_balance not in model:
                model[new_balance] = {}
            model[current_balance][action] = new_balance
        elif action == "withdraw":
            amount = hypothesis.example().draw(st.floats(min_value=0, max_value=current_balance))
            bank.withdraw(account_number, amount)
            new_balance = bank.get_balance(account_number)
            if new_balance not in model:
                model[new_balance] = {}
            model[current_balance][action] = new_balance
if __name__ == "__main__":
    hypothesis.main()
