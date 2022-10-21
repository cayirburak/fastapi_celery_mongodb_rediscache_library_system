from pymongo import MongoClient
from config_settings import Settings
setting = Settings()

client = MongoClient(setting.mongodb_conn_string)
conn = client.b2metric