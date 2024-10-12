import asyncio
import logging
import sys

from aiogram import html
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from config import API_TOKEN

from bot_worker.main_func import (
    bot_start,
    generate_key_logic,
)

from db_worker.db_func import (
    connect_sqlite_db,
    save_and_close_sqlite_db,
    add_user,
) 


TOKEN = API_TOKEN

db_connector = connect_sqlite_db("bot.db", True)


async def main() -> None:
    if db_connector:
        sqlite_cursor, sqlite_connector = db_connector
        bot, dp = await bot_start(TOKEN)
        
        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="My Clone Army", callback_data="My Clone Army"),
                InlineKeyboardButton(text="Chain Cube 2048", callback_data="Chain Cube 2048"), 
            ],
            [
                InlineKeyboardButton(text="Train Miner", callback_data="Train Miner"),
                InlineKeyboardButton(text="Bike Ride 3D", callback_data="Bike Ride 3D"),
            ],
            [
                InlineKeyboardButton(text="Merge Away", callback_data="Merge Away"),
                InlineKeyboardButton(text="Twerk Race 3D", callback_data="Twerk Race 3D"),
            ]
        ])
    else:
        print("DB ERROR!")
        exit()

    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        """
        This handler receives messages with `/start` command
        """
        user_id = message.from_user.id
        add_user(sqlite_cursor, sqlite_connector, user_id)
        sent_mess = await message.answer(
            (
                f"Hello, {html.bold(message.from_user.full_name)}!\n"
                "There are 4 keys available per day for each game."
            ),
            reply_markup=inline_keyboard
        )

    @dp.message(Command("help"))
    async def help_command(message: Message) -> None:

        await message.answer(
            "Command: /start - start app.\n"
            "Command: /about - info about developer :)."
        )

    @dp.message(Command("about"))
    async def donate_command(message: Message) -> None:
        await message.answer(
            "Conntact with dev - tg '@dev_for_you'.\n" 
            "If there are any errors or problems, or just to chat, write here.\n"
            "If you need a similar bot, write to me, can help you."
        )

    @dp.callback_query(
        lambda callback_query: callback_query.data in [
            "My Clone Army", 
            "Chain Cube 2048", 
            "Train Miner", 
            "Bike Ride 3D", 
            "Merge Away", 
            "Twerk Race 3D"
        ]
    )
    async def my_clone_army_handler(callback_query: CallbackQuery):
        await generate_key_logic(
            callback_query, 
            sqlite_cursor, 
            sqlite_connector, 
            inline_keyboard
        )
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        save_and_close_sqlite_db(sqlite_connector)
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    