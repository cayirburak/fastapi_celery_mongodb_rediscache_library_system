from fastapi import APIRouter

from models.borrowed_books import Borrowed_Book
from tasks import book_borrow_task, get_all_borrowed_books, find_borrowed_books, update_borrowed_books, delete_borrowed_books
borrowed_book = APIRouter()

@borrowed_book.get('/borrowed_book/')
async def find_all_borrowed_books():
    try:
        task = get_all_borrowed_books.delay()
        return task.get()
    except Exception as e:
        print("Bir hata meydana geldi : {}".format(e))
        return ("Bir hata meydana geldi : {}".format(e))

@borrowed_book.get('/borrowed_book/{id}')
async def find_one_borrowed_book(id):
    try:
        task = find_borrowed_books.delay(id)
        return task.get()
    except Exception as e:
        print("Bir hata meydana geldi : {}".format(e))
        return ("Bir hata meydana geldi : {}".format(e))

@borrowed_book.post('/borrowed_book/')
async def create_borrowed_book(borrowed_book: Borrowed_Book):
    try:
        task = book_borrow_task.delay(
            {
              "book": borrowed_book.book,
              "user": borrowed_book.user,
              "until_date": borrowed_book.until_date
            }
        )
        return "Ödünç alma isteği gönderildi"
    except Exception as e:
        print("Hata : {}".format(e))
        return("Hata : {}".format(e))

@borrowed_book.put('/borrowed_book/{id}')
async def update_borrowed_book(id, borrowed_book: Borrowed_Book):
    try:
        task = update_borrowed_books.delay(id,{
              "book": borrowed_book.book,
              "user": borrowed_book.user,
              "until_date": borrowed_book.until_date
            })
        return task.get()
    except Exception as e:
        print("Hata : {}".format(e))
        return("Hata : {}".format(e))

@borrowed_book.delete('/borrowed_book/{id}')
async def delete_borrowed_book(id):
    try:
        task = delete_borrowed_books.delay(id)
        return task.get()
    except Exception as e:
        print("Hata : {}".format(e))
        return("Hata : {}".format(e))