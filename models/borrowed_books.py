from pydantic import BaseModel
import datetime

class Borrowed_Book(BaseModel):
    book: str
    user: str
    until_date: datetime.datetime
