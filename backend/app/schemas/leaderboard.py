from typing import List

from pydantic import BaseModel


class LeaderboardEntryOut(BaseModel):
    rank: int
    username: str
    xp: int


class LeaderboardOut(BaseModel):
    entries: List[LeaderboardEntryOut]
    current_user_rank: int