import sqlite3

from db_func import (
    connect_sqlite_db,
    save_and_close_sqlite_db,
)


USER_TABLE = """
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        first_launch_time TEXT
    )
"""
GAME_TABLE = """
    CREATE TABLE IF NOT EXISTS game (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game_name TEXT,
        launch_count INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
"""


def create_table(sqlite_executor: sqlite3.Cursor, table_data: str) -> None:
    sqlite_executor.execute(table_data)


def create_db(file_name: str) -> None:
    sq_db, conn = connect_sqlite_db(file_name)
    create_table(sq_db, USER_TABLE)
    create_table(sq_db, GAME_TABLE)
    save_and_close_sqlite_db(conn)
    

def main() -> None:
    create_db("bot.db")
    

if __name__ == "__main__":
    main()