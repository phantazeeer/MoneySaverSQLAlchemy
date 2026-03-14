from app.db.database import get_session


async def create_user_table():
    conn = await get_session()
    await conn.execute("""CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    balance INTEGER NOT NULL DEFAULT 0,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    goal_name TEXT,
    goal_value INTEGER,
    created_at TEXT);""")
