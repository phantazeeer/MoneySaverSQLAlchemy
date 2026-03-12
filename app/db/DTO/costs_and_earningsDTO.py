from pydantic import BaseModel
from datetime import datetime

class CostsAndEarningsDTO(BaseModel):
    id: int
    user_id: int
    value: int
    comment: str | None = None
    created_at: datetime