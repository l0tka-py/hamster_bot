import asyncio
import sqlite3

from datetime import datetime, timedelta

from aiogram.types import CallbackQuery
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, BotCommand, InlineKeyboardMarkup

from hum_keys.key_generator import generate_keys
from db_worker.db_func import (
    register_game_launch,
) 

CLICK_LIMIT = 1
user_clicks = {}
TIME_WINDOW = timedelta(minutes=2)

async def bot_start(token: str) -> tuple[Bot, Dispatcher]:
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands([
        BotCommand(command="/start", description="Bot start"),
        BotCommand(command="/help", description="Help menu"),
        BotCommand(command="/about", description="About dev :)"),
    ])
    dp = Dispatcher()
    return bot, dp

def checking_number_clicks(user_id: str) -> bool:
    current_time = datetime.now()
    user_data = user_clicks.get(user_id)
    if user_data is None or (current_time - user_data["last_click_time"] > TIME_WINDOW):
        print("here")
        user_data = {
            "click_count": 0,
            "last_click_time": datetime.now()
        }
    user_data["click_count"] += 1
    user_clicks[user_id] = user_data
    if user_data["click_count"] > CLICK_LIMIT:
        return False
    return True
        

async def generate_key_logic(
    callback_query: CallbackQuery,
    sqlite_cursor: sqlite3.Cursor,
    sqlite_connector: sqlite3.Connection,
    inline_keyboard: InlineKeyboardMarkup
) -> None:
    user_id = callback_query.from_user.id
    
    if not checking_number_clicks(user_id):
        await callback_query.answer(
            "To many requests!\n"
            "Wait 1 minutes for next key gen request!", 
            cache_time=10,
        )
        return
    
    if not register_game_launch(
        sqlite_cursor,
        sqlite_connector,
        user_id,
        callback_query.data
    ):
        await callback_query.answer(
            f"The key limit for {callback_query.data} has been exceeded.",
            cache_time=10,
        )
        return
    
    await answer_message_and_run_key_gen(
        callback_query,
        callback_query.data
    )
    await callback_query.message.answer(
        (
            f"Choose next!"
        ),
        reply_markup=inline_keyboard
    )


async def answer_message_and_run_key_gen(
    callback_query: CallbackQuery,
    game_name: str
) -> None:
    await callback_query.answer("Start...")
    await callback_query.message.answer(f"{game_name} key generation...\nMay take more than 5 minutes...")
    key = await asyncio.to_thread(generate_keys, 1, game_name.replace(" ", ""))
    if key:
        await callback_query.message.answer(f"{game_name} key: `{key[0]}`", parse_mode='MarkdownV2')
        return
    await callback_query.message.answer(f"Key generation error, try using the bot in a couple of minutes!")
