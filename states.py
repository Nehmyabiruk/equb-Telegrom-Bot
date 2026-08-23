from aiogram.fsm.state import State, StatesGroup


# =========================================================
# ETHIO CAR EQUB REGISTRATION STATES
# =========================================================

class RegistrationStates(StatesGroup):

    # Language selection
    language = State()

    # Payment for self or another person
    payment_for = State()

    # Participant information
    full_name = State()
    phone = State()

    # Payment information
    payment_method = State()
    receipt = State()
    transaction_reference = State()

    # Waiting for admin verification
    waiting_for_admin = State()