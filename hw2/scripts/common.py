"""Общие настройки демонстрационных Python-скриптов."""
import os
from pprint import pprint

from pymongo import MongoClient


def connect():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"),
                         serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    return client, client["video_lab"]


def show(title, documents):
    print(f"\n{title}")
    for document in documents:
        pprint(document, sort_dicts=False, width=100)
