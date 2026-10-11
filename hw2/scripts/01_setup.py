"""Создание схемы и тестовых данных. Удаляет только базу video_lab."""
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from common import connect


def oid(prefix, number):
    return ObjectId(f"{prefix}{number:022x}")


def date(year, month, day):
    return datetime(year, month, day, tzinfo=timezone.utc)


def validator(required, properties):
    return {"$jsonSchema": {"bsonType": "object", "required": required,
                            "properties": properties}}


client, db = connect()
client.drop_database("video_lab")

db.create_collection("users", validator=validator(
    ["username", "email", "joinedAt", "profile"], {
        "username": {"bsonType": "string", "minLength": 3, "maxLength": 30},
        "email": {"bsonType": "string", "pattern": r"^[^@ ]+@[^@ ]+\.[^@ ]+$"},
        "joinedAt": {"bsonType": "date"},
        "profile": {"bsonType": "object", "required": ["displayName", "country"],
                    "properties": {"displayName": {"bsonType": "string", "minLength": 2},
                                   "country": {"bsonType": "string", "minLength": 2}}},
        "interests": {"bsonType": "array", "items": {"bsonType": "string"}},
    }), validationLevel="strict", validationAction="error")

db.create_collection("channels", validator=validator(
    ["ownerId", "name", "topic", "createdAt", "stats"], {
        "ownerId": {"bsonType": "objectId"},
        "name": {"bsonType": "string", "minLength": 3},
        "topic": {"enum": ["Технологии", "Наука", "Кулинария", "Путешествия"]},
        "createdAt": {"bsonType": "date"},
        "stats": {"bsonType": "object", "required": ["subscriberCount"],
                  "properties": {"subscriberCount": {"bsonType": "number", "minimum": 0}}},
    }), validationLevel="strict", validationAction="error")

db.create_collection("videos", validator=validator(
    ["channelId", "title", "category", "tags", "durationSeconds", "views",
     "likes", "publishedAt", "status"], {
        "channelId": {"bsonType": "objectId"},
        "title": {"bsonType": "string", "minLength": 5},
        "category": {"enum": ["Технологии", "Наука", "Кулинария", "Путешествия"]},
        "tags": {"bsonType": "array", "minItems": 1,
                 "items": {"bsonType": "string"}},
        "durationSeconds": {"bsonType": "number", "minimum": 1},
        "views": {"bsonType": "number", "minimum": 0},
        "likes": {"bsonType": "number", "minimum": 0},
        "publishedAt": {"bsonType": "date"},
        "status": {"enum": ["published", "draft"]},
        "chapters": {"bsonType": "array", "items": {
            "bsonType": "object", "required": ["title", "startSecond"],
            "properties": {"title": {"bsonType": "string"},
                           "startSecond": {"bsonType": "number", "minimum": 0}}}},
    }), validationLevel="strict", validationAction="error")

db.create_collection("comments", validator=validator(
    ["videoId", "userId", "text", "createdAt", "likes"], {
        "videoId": {"bsonType": "objectId"},
        "userId": {"bsonType": "objectId"},
        "text": {"bsonType": "string", "minLength": 2},
        "createdAt": {"bsonType": "date"},
        "likes": {"bsonType": "number", "minimum": 0},
    }), validationLevel="strict", validationAction="error")

db.create_collection("subscriptions", validator=validator(
    ["userId", "channelId", "createdAt", "notificationsEnabled"], {
        "userId": {"bsonType": "objectId"},
        "channelId": {"bsonType": "objectId"},
        "createdAt": {"bsonType": "date"},
        "notificationsEnabled": {"bsonType": "bool"},
    }), validationLevel="strict", validationAction="error")

names = ["Анна", "Борис", "Вера", "Глеб", "Дарья", "Егор", "Жанна", "Зоя",
         "Илья", "Кира", "Лев", "Мария"]
countries = ["Россия", "Казахстан", "Беларусь"]
categories = ["Технологии", "Наука", "Кулинария", "Путешествия"]
channel_names = ["Код и кофе", "Физика рядом", "Домашняя кухня", "Маршруты мира",
                 "Мобильный мир", "Космос просто", "Вкусный вечер", "Город пешком",
                 "Данные на практике", "Биология вокруг", "Хлеб и тесто", "Поезда и страны"]
titles = ["Как устроены базы данных", "Почему небо голубое", "Паста за двадцать минут",
          "Выходные в Казани", "Выбор смартфона", "Путешествие по Солнечной системе",
          "Домашний борщ", "Прогулка по Петербургу", "Индексы в MongoDB",
          "Как работает иммунитет", "Печём домашний хлеб", "Поездом через Кавказ",
          "Сравнение языков программирования", "Мифы о квантовой физике",
          "Идеальный завтрак", "Маршрут по Алтаю", "Безопасность приложений",
          "Наблюдаем звёзды"]
tags = [
    ["mongodb", "базы данных"], ["физика", "образование"], ["рецепты", "паста"],
    ["россия", "маршруты"], ["смартфоны", "обзор"], ["космос", "наука"],
    ["рецепты", "суп"], ["город", "прогулка"], ["mongodb", "индексы"],
    ["биология", "здоровье"], ["выпечка", "рецепты"], ["поезд", "путешествия"],
    ["код", "сравнение"], ["физика", "наука"], ["завтрак", "рецепты"],
    ["алтай", "маршруты"], ["безопасность", "код"], ["астрономия", "наука"],
]

db.users.insert_many([
    {"_id": oid("11", i + 1), "username": f"user{i + 1}",
     "email": f"user{i + 1}@example.test", "joinedAt": date(2025, i + 1, i + 1),
     "profile": {"displayName": name, "country": countries[i % 3]},
     "interests": [categories[i % 4], categories[(i + 1) % 4]]}
    for i, name in enumerate(names)
])
db.channels.insert_many([
    {"_id": oid("22", i + 1), "ownerId": oid("11", i + 1), "name": name,
     "topic": categories[i % 4], "createdAt": date(2025, 2, i + 1),
     "stats": {"subscriberCount": 100 + i * 37}}
    for i, name in enumerate(channel_names)
])
db.videos.insert_many([
    {"_id": oid("33", i + 1), "channelId": oid("22", (i % 12) + 1),
     "title": title, "category": categories[i % 4], "tags": tags[i],
     "durationSeconds": 360 + i * 80, "views": 900 + i * 475,
     "likes": 35 + i * 19, "publishedAt": date(2026, 1, i + 1),
     "status": "published", "chapters": [
         {"title": "Введение", "startSecond": 0},
         {"title": "Главная часть", "startSecond": 90}]}
    for i, title in enumerate(titles)
])
comment_texts = ["Отличное объяснение!", "Полезный пример", "Спасибо за выпуск",
                 "Жду продолжения", "Возьму на заметку", "Очень интересно"]
db.comments.insert_many([
    {"_id": oid("44", i + 1), "videoId": oid("33", (i % 18) + 1),
     "userId": oid("11", ((i + 2) % 12) + 1), "text": comment_texts[i % 6],
     "createdAt": date(2026, 2, (i % 24) + 1), "likes": i % 7}
    for i in range(24)
])
db.subscriptions.insert_many([
    {"_id": oid("55", i + 1), "userId": oid("11", (i % 12) + 1),
     "channelId": oid("22", ((i + 1 + i // 12) % 12) + 1),
     "createdAt": date(2026, 3, (i % 24) + 1),
     "notificationsEnabled": i % 3 != 0}
    for i in range(24)
])

db.users.create_index([("email", ASCENDING)], unique=True, name="email_unique")
db.videos.create_index([("category", ASCENDING), ("views", DESCENDING)],
                       name="category_views_idx")
db.comments.create_index([("videoId", ASCENDING), ("createdAt", DESCENDING)],
                         name="video_comments_idx")
db.subscriptions.create_index([("userId", ASCENDING), ("channelId", ASCENDING)],
                              unique=True, name="one_subscription_per_channel")

print("Создана база video_lab:")
for collection_name in ["users", "channels", "videos", "comments", "subscriptions"]:
    print(f"{collection_name}: {db[collection_name].count_documents({})}")
client.close()
