# commands.py - модуль в якому оголошені всі необхідні команди(та їх фільтри)
from aiogram.types.bot_command import BotCommand
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State


class MovieStates(StatesGroup):
    search_actor = State()


FILMS_COMMAND = Command('films')

# commands.py - модуль в якому оголошені всі необхідні команди(та їх фільтри)

FILMS_COMMAND = Command('films')
START_COMMAND = Command('start')

FILMS_BOT_COMMAND = BotCommand(
    command='films', description="Перегляд списку фільмів")
START_BOT_COMMAND = BotCommand(command='start', description="Почати розмову")
FILM_CREATE_COMMAND = Command("create_film")
BOT_COMMANDS = [
    BotCommand(command="films", description="Перегляд списку фільмів"),
    BotCommand(command="start", description="Почати розмову"),
    BotCommand(command="delete_movie", description="Видалення фільму"),
    BotCommand(command="filter_movie", description="Фільтрувати фільми"),
    BotCommand(command="create_film", description="Додати новий фільм"),
    BotCommand(command="search_movie", description="Знайти фільм"),
    BotCommand(
        command="search_by_actor",
        description="Пошук фільмів за актором"
    ),
    BotCommand(command="edit_movie", description="Редагувати фільм"),
]
FILM_SEARCH_COMMAND = Command("search_movie")
FILM_FILTER_COMMAND = Command("filter_movie")
FILM_DELETE_COMMAND = Command("delete_movie")
FILM_SEARCH_BY_ACTOR_COMMAND = Command("search_by_actor")
FILM_EDIT_COMMAND = Command("edit_movie")
