from app.db.database import get_session
from datetime import datetime, timezone


class CostsAndEarningsService:
    async def init_session(self):
        self.conn = await get_session()

    async def add_record(self, user_id: int, operation_type: int, value: int, comment: str | None = None):
        await self.conn.execute(
            """INSERT INTO costs_and_earnings (user_id, operation_type, value, comment, created_at) VALUES (?, ?, ?, ?, ?)""",
            (user_id, operation_type, value, comment, datetime.now(timezone.utc)))
        await self.conn.execute("""UPDATE user SET balance = balance + ? WHERE id = ?""",
                                ((-1) ** operation_type * value, user_id))
        await self.conn.commit()

    async def delete_record(self, id: int):
        record = await (await self.conn.execute("""SELECT * FROM costs_and_earnings WHERE id = ?""", (id,))).fetchone()
        user = await self.conn.execute("""SELECT * FROM user WHERE id = ?""", (record[1],))
        await self.conn.execute("""UPDATE user SET balance = balance - ? WHERE id = ?""",
                                ((-1) ** record[2] * record[3], user[0]))
        await self.conn.execute("""DELETE FROM costs_and_earnings WHERE id = ?""", (id,))
        await self.conn.commit()

    async def get_records_by(self, id: str | None = None, user_id: int | None = None):
        if id:
            cursor = await self.conn.execute("""SELECT * FROM costs_and_earnings WHERE id = ?""", (id,))
        elif user_id:
            cursor = await self.conn.execute("""SELECT * FROM costs_and_earnings WHERE user_id = ?""", (user_id,))
        else:
            raise Exception('incorrect using get_records_by')
        res = await cursor.fetchall()
        return res

    async def update_record(self, id: int, operation_type: int, value: int, comment: str | None = None):
        record = await (await self.conn.execute("""SELECT * FROM costs_and_earnings WHERE id = ?""", (id,))).fetchone()
        if not operation_type:
            operation_type = record[2]
        if not value:
            value = record[3]
        if not comment:
            comment = record[4]
        await self.conn.execute(
            """UPDATE costs_and_earnings SET operation_type = ?, value = ?, comment = ? WHERE id = ?""",
            (operation_type, value, comment, id))
        await self.conn.commit()
