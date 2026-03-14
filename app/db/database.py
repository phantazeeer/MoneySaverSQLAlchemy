from aiosqlite import connect, Connection


async def get_session(path: str = './app/db/database.db') -> Connection:
    conn = await connect(path)
    settings = True # TODO: добавить переменные окружения
    if settings:
        await conn.set_trace_callback(print)
    await conn.execute("PRAGMA foreign_keys = ON")
    return conn
