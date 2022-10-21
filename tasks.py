from celery import Celery
from celery.utils.log import get_task_logger
from models.borrowed_books import Borrowed_Book
from config.db import conn
from config.redis import redis_connect, get_routes_from_cache, set_routes_to_cache, delete_routes_from_cache
from schemas.user import serializeDict, serializeList
from datetime import datetime
from bson import ObjectId
import json
from config_settings import Settings
setting = Settings()

celery = Celery(
    __name__,
    broker="redis://" + setting.redis_host + ":6379/0",
    backend="redis://" + setting.redis_host + ":6379/0"
)

@celery.task(name='get_all_borrowed_books')
def get_all_borrowed_books():
    try:
        data = get_routes_from_cache(key="all_borrowed_books")
        # If cache is found then serves the data from cache
        if data is not None:
            print("find_all_borrowed_books cache'den alınıyor...")
            data = json.loads(data)
            return data
        else:
            # If cache is not found then sends request to API
            print("find_all_borrowed_books cache'de yok cache'e yazılıyor...")
            data = serializeList(conn.borrowed_book.find())
            # This block sets saves the response to redis and serves it directly
            if len(data) > 0:
                data = json.dumps(data)
                state = set_routes_to_cache(key="all_borrowed_books", value=data)
                if state is True:
                    return json.loads(data)
        return serializeList(conn.borrowed_book.find())
    except Exception as e:
        print("Bir hata meydana geldi : {}".format(e))
        return ("Bir hata meydana geldi : {}".format(e))

@celery.task(name='find_borrowed_books')
def find_borrowed_books(id):
    try:
        data = get_routes_from_cache(key=id)

        # If cache is found then serves the data from cache
        if data is not None:
            print("find_one_borrowed_book cache'den alınıyor...")
            data = json.loads(data)
            return data

        else:
            # If cache is not found then sends request to API
            print("find_one_borrowed_book cache'de yok cache'e yazılıyor...")
            data = serializeDict(conn.borrowed_book.find_one({"_id":ObjectId(id)}))

            # This block sets saves the response to redis and serves it directly
            if len(data) > 0:
                data = json.dumps(data)
                state = set_routes_to_cache(key=id, value=data)

                if state is True:
                    return json.loads(data)
        return serializeDict(conn.borrowed_book.find_one({"_id":ObjectId(id)}))
    except TypeError:
        return "Kullanıcı Mevcut değil"
    except Exception as e:
        print("Bir hata meydana geldi : {}".format(e))
        return ("Bir hata meydana geldi : {}".format(e))

@celery.task(name='book_borrow_task')
def book_borrow_task(borrowed_book: Borrowed_Book):
    try:
        print(borrowed_book['book'])
        check_book_borrowed = conn.borrowed_book.find_one( { 'book': borrowed_book['book'] } )
        print(check_book_borrowed)
        if check_book_borrowed != None:
            until_date = check_book_borrowed['until_date'].replace("T"," ").replace("Z","")
            until_date = datetime.strptime(until_date, '%Y-%m-%d %H:%M:%S.%f')
            now_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
            check_time = until_date > now_date
            diff_time = until_date - now_date
            if check_time:
                print("Kitap ödünç alınamaz {} gün {} saat {} dakika sonra alabilirsiniz".format(diff_time.days, diff_time.seconds//3600, ((diff_time.seconds//60) % 60)))
                return "Kitap Ödünç Alınmış"
        else:
            print("Kitap ödünç alınması uygun")
        delete_routes_from_cache('all_borrowed_books')
        if check_book_borrowed != None:
            conn.borrowed_book.delete_many({'book': check_book_borrowed['book']})
        check_exist_book = conn.book.find_one( { 'title': borrowed_book['book'] } )
        check_exist_user = conn.user.find_one( { 'name': borrowed_book['user'] } )
        if check_exist_user and check_exist_book:
            print("Kitap ve Kullanıcı Mevcut Ödünç işlemi gerçekleştirilebilir.")
            conn.borrowed_book.insert_one(borrowed_book)
        else:
            print("Kitap ve Kullanıcı Mevcut değil Ödünç işlemi gerçekleştirilemez.")
            return "Kullanıcı veya Kitap mevcut değil"
        return serializeList(conn.borrowed_book.find())
    except Exception as e:
        print("Bir hata meydana geldi : {}".format(e))
        return ("Bir hata meydana geldi : {}".format(e))

@celery.task(name='update_borrowed_books')
def update_borrowed_books(id, borrowed_book: Borrowed_Book):
    try:
        delete_routes_from_cache('all_borrowed_books')
        conn.borrowed_book.find_one_and_update({"_id": ObjectId(id)}, {
            "$set": dict(borrowed_book)
        })
        return serializeDict(conn.borrowed_book.find_one({"_id":ObjectId(id)}))
    except Exception as e:
        print("Bir hata meydana geldi : {}".format(e))
        return ("Bir hata meydana geldi : {}".format(e))

@celery.task(name='delete_borrowed_books')
def delete_borrowed_books(id):
    try:
        delete_routes_from_cache('all_borrowed_books')
        return serializeDict(conn.borrowed_book.find_one_and_delete({"_id":ObjectId(id)}))
    except Exception as e:
        print("Bir hata meydana geldi : {}".format(e))
        return ("Bir hata meydana geldi : {}".format(e))