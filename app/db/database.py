from aiosqlite import connect


async def get_session(path: str = './app/db/database.db'):
    conn = await connect(path)
    return conn
