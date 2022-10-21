from fastapi import APIRouter

from models.book import Book
from config.db import conn
from config.redis import redis_connect, get_routes_from_cache, set_routes_to_cache, delete_routes_from_cache
from schemas.user import serializeDict, serializeList
from bson import ObjectId
import json
book = APIRouter()

@book.get('/book/')
async def find_all_books():
    try:
        data = get_routes_from_cache(key="all_books")

        # If cache is found then serves the data from cache
        if data is not None:
            print("find_all_books cache'den alınıyor...")
            data = json.loads(data)
            return data

        else:
            # If cache is not found then sends request to API
            print("find_all_books cache'de yok cache'e yazılıyor...")
            data = serializeList(conn.book.find())

            # This block sets saves the response to redis and serves it directly
            if len(data) > 0:
                data = json.dumps(data)
                state = set_routes_to_cache(key="all_books", value=data)

                if state is True:
                    return json.loads(data)
        return serializeList(conn.book.find())
    except Exception as e:
        return e

@book.get('/book/{id}')
async def find_one_book(id):
    try:
        data = get_routes_from_cache(key=id)

        # If cache is found then serves the data from cache
        if data is not None:
            print("find_one_book cache'den alınıyor...")
            data = json.loads(data)
            return data

        else:
            # If cache is not found then sends request to API
            print("find_one_book cache'de yok cache'e yazılıyor...")
            data = serializeDict(conn.book.find_one({"_id":ObjectId(id)}))

            # This block sets saves the response to redis and serves it directly
            if len(data) > 0:
                data = json.dumps(data)
                state = set_routes_to_cache(key=id, value=data)

                if state is True:
                    return json.loads(data)
        return serializeDict(conn.book.find_one({"_id":ObjectId(id)}))
    except TypeError:
        return "Kitap Mevcut değil"
    except Exception as e:
        return e

@book.post('/book/')
async def create_book(book: Book):
    try:
        delete_routes_from_cache('all_books')
        conn.book.insert_one(dict(book))
        return serializeList(conn.book.find())
    except Exception as e:
        return e

@book.put('/book/{id}')
async def update_book(id, book: Book):
    try:
        conn.book.find_one_and_update({"_id": ObjectId(id)}, {
            "$set": dict(book)
        })
        return serializeDict(conn.book.find_one({"_id":ObjectId(id)}))
    except Exception as e:
        return e

@book.delete('/book/{id}')
async def delete_book(id):
    try:
        delete_routes_from_cache('all_books')
        return serializeDict(conn.book.find_one_and_delete({"_id":ObjectId(id)}))
    except Exception as e:
        return e