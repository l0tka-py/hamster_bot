import sqlite3
import os
from datetime import datetime


def connect_sqlite_db(
    file_name: str, 
    is_exist: bool = False
) -> tuple[sqlite3.Cursor, sqlite3.Connection] | None:
    if is_exist:
        if not os.path.exists(file_name):
            return None
    
    connector = sqlite3.connect(file_name)
    
    return connector.cursor(), connector


def save_and_close_sqlite_db(sqlite_connector: sqlite3.Connection) -> None:
    sqlite_connector.commit()
    sqlite_connector.close()
    

def add_user(
    sqlite_cursor: sqlite3.Cursor,
    sqlite_connector: sqlite3.Connection,
    user_id: str
) -> None:

    # Проверяем, существует ли пользователь
    sqlite_cursor.execute("SELECT id FROM user WHERE id = ?", (user_id,))
    if sqlite_cursor.fetchone() is None:
        # Если пользователь не существует, добавляем его
        first_launch_time = datetime.now().strftime("%Y-%m-%d")
        sqlite_cursor.execute("INSERT INTO user (id, first_launch_time) VALUES (?, ?)", (user_id, first_launch_time))
        sqlite_connector.commit()


# Функция для регистрации запуска игры
def register_game_launch(
    sqlite_cursor: sqlite3.Cursor, 
    sqlite_connector: sqlite3.Connection, 
    user_id: str, 
    game_name: str
) -> bool:

    # Проверяем, существует ли запись о запуске игры для этого пользователя
    sqlite_cursor.execute(
        "SELECT launch_count FROM game WHERE user_id = ? AND game_name = ?",
        (user_id, game_name)
    )
    result = sqlite_cursor.fetchone()

    if result is None:
        # Если такой записи нет, создаем новую
        sqlite_cursor.execute(
            "INSERT INTO game (user_id, game_name, launch_count) VALUES (?, ?, ?)",
            (user_id, game_name, 1)
        )
    else:
        if result[0] == 4:
            if not update_user_launch_date(sqlite_cursor, sqlite_connector, user_id):
                return False
            sqlite_cursor.execute(
                "UPDATE game SET launch_count = ? WHERE user_id = ? AND game_name = ?", 
                (1, user_id, game_name)
            )
            return True
        # Если запись существует, увеличиваем счетчик запусков
        new_count = result[0] + 1
        sqlite_cursor.execute(
            "UPDATE game SET launch_count = ? WHERE user_id = ? AND game_name = ?", 
            (new_count, user_id, game_name)
        )

    sqlite_connector.commit()
    return True
    

def update_user_launch_date(
    sqlite_cursor: sqlite3.Cursor, 
    sqlite_connector: sqlite3.Connection, 
    user_id: str
) -> bool:

    # Получаем текущую дату
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Проверяем, существует ли пользователь
    sqlite_cursor.execute(
        "SELECT first_launch_time FROM user WHERE id = ?",
        (user_id,)
    )
    result = sqlite_cursor.fetchone()

    if result:
        stored_date = result[0]
        if stored_date != current_date:
            # Если даты отличаются, обновляем дату в базе данных
            sqlite_cursor.execute(
                "UPDATE user SET first_launch_time = ? WHERE id = ?",
                (current_date, user_id)
            )
            sqlite_connector.commit()
            return True
        else:
            return False
    return False
