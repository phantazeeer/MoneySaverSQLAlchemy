from pydantic import BaseModel
from datetime import datetime

class CostsAndEarningsDTO(BaseModel):
    id: int
    user_id: int
    operation_type: int
    value: int
    comment: str | None = None
    created_at: datetime