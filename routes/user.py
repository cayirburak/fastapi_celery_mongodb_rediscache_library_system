from fastapi import APIRouter

from models.user import User
from config.db import conn
from config.redis import get_routes_from_cache, set_routes_to_cache, delete_routes_from_cache
from schemas.user import serializeDict, serializeList
from bson import ObjectId
import json

user = APIRouter()

@user.get('/user/')
async def find_all_users():
    try:
        data = get_routes_from_cache(key="all_users")

        # If cache is found then serves the data from cache
        if data is not None:
            print("find_all_users cache'den alınıyor...")
            data = json.loads(data)
            return data

        else:
            # If cache is not found then sends request to API
            print("find_all_users cache'de yok cache'e yazılıyor...")
            data = serializeList(conn.user.find())

            # This block sets saves the response to redis and serves it directly
            if len(data) > 0:
                data = json.dumps(data)
                state = set_routes_to_cache(key="all_users", value=data)

                if state is True:
                    return json.loads(data)
        return serializeList(conn.user.find())
    except Exception as e:
        return e

@user.get('/user/{id}')
async def find_one_user(id):
    try:
        data = get_routes_from_cache(key=id)

        # If cache is found then serves the data from cache
        if data is not None:
            print("find_one_user cache'den alınıyor...")
            data = json.loads(data)
            return data

        else:
            # If cache is not found then sends request to API
            print("find_one_user cache'de yok cache'e yazılıyor...")
            data = serializeDict(conn.user.find_one({"_id":ObjectId(id)}))

            # This block sets saves the response to redis and serves it directly
            if len(data) > 0:
                data = json.dumps(data)
                state = set_routes_to_cache(key=id, value=data)

                if state is True:
                    return json.loads(data)
        return serializeDict(conn.user.find_one({"_id":ObjectId(id)}))
    except TypeError:
        return "Kullanıcı Mevcut değil"
    except Exception as e:
        return e

@user.post('/user/')
async def create_user(user: User):
    try:
        delete_routes_from_cache('all_users')
        conn.user.insert_one(dict(user))
        return serializeList(conn.user.find())
    except Exception as e:
        return e

@user.put('/user/{id}')
async def update_user(id, user: User):
    try:
        conn.user.find_one_and_update({"_id": ObjectId(id)}, {
            "$set": dict(user)
        })
        return serializeDict(conn.user.find_one({"_id":ObjectId(id)}))
    except Exception as e:
        return e

@user.delete('/user/{id}')
async def delete_user(id):
    try:
        delete_routes_from_cache('all_users')
        return serializeDict(conn.user.find_one_and_delete({"_id":ObjectId(id)}))
    except Exception as e:
        return e