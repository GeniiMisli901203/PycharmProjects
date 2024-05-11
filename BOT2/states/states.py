from aiogram.fsm.state import State, StatesGroup


class FSMSettings(StatesGroup):
    set_age = State()
    set_sex = State()
    set_location = State()
    set_currency = State()
    set_bio = State()

    edit_age = State()
    edit_sex = State()
    edit_location = State()
    edit_currency = State()
    edit_bio = State()


class FSMTrip(StatesGroup):
    set_name = State()
    set_descriptipon = State()
    set_destination = State()
    set_dates = State()

    edit_name = State()
    edit_descriptipon = State()


class FSMNote(StatesGroup):
    set_private = State()
    set_note = State()


class FSMFriend(StatesGroup):
    add_friend = State()


class FSMLocation(StatesGroup):
    add_geo = State()
    set_location_dates = State()


class FSMExpense(StatesGroup):
    set_name = State()
    set_cost = State()
    set_debtors = State()

    add_debtor = State()
    edit_name = State()
    edit_cost = State()


class FSMCurrency(StatesGroup):
    select_currency = State()
    set_amount = State()
