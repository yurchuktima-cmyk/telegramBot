import asyncio
import logging
import sys
from data import get_films
from functions import save_image
from keyboards import films_keyboard_markup
from keyboards import films_keyboard_markup, FilmCallback
from aiogram.types import Message, CallbackQuery
from data import edit_film
from external import async_log_function_call

# from os import getenv
from config import BOT_TOKEN as TOKEN

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from models import Film
from aiogram.types import FSInputFile
from commands import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from data import *

# Bot token can be obtained via https://t.me/BotFather
# TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

from aiogram.fsm.state import StatesGroup, State


class FilmForm(StatesGroup):
    name = State()
    description = State()
    rating = State()
    genre = State()
    actors = State()
    poster = State()


class MovieStates(StatesGroup):
    search_query = State()
    filter_criteria = State()
    delete_query = State()
    edit_query = State()
    edit_description = State()
    search_actor = State()
    search_qwery = State()


dp = Dispatcher()

# запускає бота
@dp.message(CommandStart())
@async_log_function_call
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"вітаю , {html.bold(message.from_user.full_name)} я бот  який допоможе тобі зібрати власну бібліотеку фільмів, натисни на /films для того щоб побачити фільми які вже є в боті !")


@dp.message(FILMS_COMMAND)
@async_log_function_call
async def films(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        f"Перелік фільмів. Натисніть на назву фільму для отримання деталей.",
        reply_markup=markup
    )


# додає фільм який вказав користувач
@dp.message(FILM_CREATE_COMMAND)
@async_log_function_call
async def film_create(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmForm.name)
    await message.answer(
        f"Введіть назву фільму.",
        reply_markup=None,
    )


@dp.message(FilmForm.name)
@async_log_function_call
async def film_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(FilmForm.description)
    await message.answer(
        f"Введіть опис фільму.")


@dp.message(FilmForm.description)
@async_log_function_call
async def film_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(FilmForm.rating)
    await message.answer(
        f"Вкажіть рейтинг фільму від 0 до 10.",)


@dp.message(FilmForm.rating)
@async_log_function_call
async def film_rating(message: Message, state: FSMContext) -> None:
    await state.update_data(rating=message.text)
    await state.set_state(FilmForm.genre)
    await message.answer(
        f"Введіть жанр фільму.")


@dp.message(FilmForm.genre)
@async_log_function_call
async def film_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(FilmForm.actors)
    await message.answer(
        text=f"Введіть акторів фільму через роздільник ', '\n"
        + html.bold("Обов'язкова кома та відступ після неї."))


@dp.message(FilmForm.actors)
@async_log_function_call
async def film_actors(message: Message, state: FSMContext) -> None:
    actors = message.text.split(",")
    actors = [actor.strip() for actor in actors]
    await state.update_data(actors=actors)
    await state.set_state(FilmForm.poster)
    await message.answer(
        f"Введіть посилання на постер фільму.")


@dp.message(FilmForm.poster)
@async_log_function_call
async def film_poster(message: Message, state: FSMContext) -> None:

    poster_value = None

    if message.photo:
        # Save Telegram file_id (best quality)
        poster_value = message.photo[-1].file_id

    elif message.document and message.document.mime_type.startswith("image/"):
        # If image is sent as document
        poster_value = message.document.file_id

    elif message.text:
        # Text fallback (URL or description)
        poster_value = message.text

    else:
        await message.answer("Надішліть постер як фото або текстом.")
        return

    data = await state.update_data(poster=poster_value)
    print(poster_value)
    film = Film(**data)
    add_film(film.model_dump())
    await state.clear()
    await message.answer(
        f"Фільм {film.name} успішно додано!")


@dp.message(FILM_SEARCH_COMMAND)
@async_log_function_call
async def search_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму для пошуку:")
    await state.set_state(MovieStates.search_query)


@dp.message(MovieStates.search_query)
@async_log_function_call
async def get_search_query(message: Message, state: FSMContext):
    query = message.text.lower()
    films = get_films()
    results = [film for film in films if query in film['name'].lower()]

    if results:
        for film in results:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено.")

    await state.clear()


@dp.callback_query(FilmCallback.filter())
@async_log_function_call
async def callb_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)

    text = f"Фільм: {film.name}\n" \
        f"Опис: {film.description}\n" \
        f"Рейтинг: {film.rating}\n" \
        f"Жанр: {film.genre}\n" \
        f"Актори: {', '.join(film.actors)}\n"

    if film.poster[:5] == "http":
        await callback.message.answer_photo(
            caption=text,
            photo=FSInputFile(
                save_image(film.poster),
                filename=f"{film.name}_poster.{film.poster.split('.')[-1]}"
            )
        )
    else:
        await callback.message.answer_photo(
            caption=text,
            photo=film.poster
        )


# фільтрує фільм за жвнром
@dp.message(FILM_FILTER_COMMAND)
@async_log_function_call
async def filter_movies(message: Message, state: FSMContext):
    await message.reply("Введіть жанр для фільтрації:")
    await state.set_state(MovieStates.filter_criteria)


@dp.message(MovieStates.filter_criteria)
@async_log_function_call
async def get_filter_criteria(message: Message, state: FSMContext):
    films = get_films()
    criteria = message.text.lower()
    filtered = list(filter(
        lambda film: criteria in film['genre'].lower() == criteria, films
    ))

    if filtered:
        for film in filtered:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено за цими критеріями.")

    await state.clear()


# видвляє фільм назву якого вказав користувач
@dp.message(FILM_DELETE_COMMAND)
@async_log_function_call
async def delete_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, який бажаєте видалити:")
    await state.set_state(MovieStates.delete_query)


@dp.message(MovieStates.delete_query)
@async_log_function_call
async def get_delete_query(message: Message, state: FSMContext):
    films = get_films()

    film_to_delete = message.text.lower()
    for film in films:
        if film_to_delete == film['name'].lower():
            delete_film(film)
            await message.reply(f"Фільм '{film['name']}' видалено.")
            await state.clear()
            return
    await message.reply("Фільм не знайдено.")
    await state.clear()


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    await bot.set_my_commands(BOT_COMMANDS)
    await dp.start_polling(bot)


# шукає фільм за актором
@dp.message(FILM_SEARCH_BY_ACTOR_COMMAND)
@async_log_function_call
async def search_by_actor(message: Message, state: FSMContext):
    await message.reply("Введіть ім'я актора для пошуку:")
    await state.set_state(MovieStates.search_actor)


@dp.message(MovieStates.search_actor)
@async_log_function_call
async def process_actor_search(message: Message, state: FSMContext):
    actor_name = message.text.lower()
    movies = get_films()

    found_movies = [
        movie["name"]
        for movie in movies
        if any(actor_name in actor.lower() for actor in movie["actors"])
    ]

    if found_movies:
        await message.reply(
            "Фільми за участю цього актора:\n" + "\n".join(found_movies)
        )
    else:
        await message.reply("Фільмів з таким актором не знайдено.")

    await state.clear()


# додає фільм до списку
@dp.message(FILM_EDIT_COMMAND)
@async_log_function_call
async def edit_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму, який бажаєте редагувати:")
    await state.set_state(MovieStates.edit_query)


@dp.message(MovieStates.edit_query)
@async_log_function_call
async def get_edit_query(message: Message, state: FSMContext):
    film_to_edit = message.text.lower()
    films = get_films()
    for film in films:
        if film_to_edit == film['name'].lower():
            await state.update_data(film=film)
            await message.reply("Введіть новий опис фільму:")
            await state.set_state(MovieStates.edit_description)
            return
    await message.reply("Фільм не знайдено.")
    await state.clear()


@dp.message(MovieStates.edit_description)
@async_log_function_call
async def update_description(message: Message, state: FSMContext):
    data = await state.get_data()
    film = data['film']
    film['description'] = message.text
    edit_film(film)
    await message.reply(f"Фільм '{film['name']}' оновлено.")
    await state.clear()


# робить ефект ехо (пересилає користувачевій йогож повідомлення)
@dp.message()
@async_log_function_call
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="log.txt")
    asyncio.run(main())

#hello