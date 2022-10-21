from fastapi import FastAPI
from routes.user import user
from routes.book import book
from routes.borrowed_books import borrowed_book
app = FastAPI()
app.include_router(user)
app.include_router(book)
app.include_router(borrowed_book)