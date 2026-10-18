from aiogram.fsm.state import State, StatesGroup

class ViewOrderStates(StatesGroup):
    WAITING_FOR_QUANTITY = State()
    WAITING_FOR_SPEED = State()
    WAITING_FOR_POST = State()
    CONFIRMING_ORDER = State()

class ViewMultipleOrderStates(StatesGroup):
    WAITING_FOR_QUANTITY = State()
    WAITING_FOR_SPEED = State()
    WAITING_FOR_POSTS = State()
    CONFIRMING_ORDERS = State()
