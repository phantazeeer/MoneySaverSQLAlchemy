from aiosqlite import connect


async def get_session(path: str = './app/db/database.db'):
    conn = await connect(path)
    settings = True # TODO: добавить переменные окружения
    if settings:
        await conn.set_trace_callback(print)
    return conn
