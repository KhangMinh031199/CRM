from pymongo import MongoClient
import settings
from collections import OrderedDict


def mongodb_create():
        
        Mongodb = MongoClient(
        settings.MONGODB_HOST,
        settings.MONGODB_PORT,
        document_class=OrderedDict,
        maxPoolSize=200,
        serverSelectionTimeoutMS=90000)

        DATABASE = Mongodb['nextify']

        DATABASE.authenticate(
        settings.MONGODB_USER,
        settings.MONGODB_PASSWORD,
        source=settings.MONGO_NAME_AUTHEN)

        return Mongodb
