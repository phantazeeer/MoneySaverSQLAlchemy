from app.db.database import get_session


async def create_costs_and_earnings_table():
    conn = await get_session()
    await conn.execute("""CREATE TABLE costs_and_earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    operation_type INTEGER NOT NULL,
    value INTEGER NOT NULL,
    comment TEXT,
    created_at TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id));""")
