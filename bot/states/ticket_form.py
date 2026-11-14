from aiogram.fsm.state import StatesGroup, State

class TicketForm(StatesGroup):
    cause = State()