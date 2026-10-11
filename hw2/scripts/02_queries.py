"""Поиск, проекция, сортировка, массивы, CRUD и отказ валидации."""
from datetime import datetime, timezone
from pprint import pprint

from pymongo import DESCENDING
from pymongo.errors import WriteError

from common import connect, show


client, db = connect()

show('1. db.videos.find({"category": "Технологии"}, {"title": 1, "views": 1, "_id": 0})',
     db.videos.find({"category": "Технологии"},
                    {"title": 1, "views": 1, "_id": 0}))

show('2. db.videos.find({"category": "Наука", "views": {"$gte": 1500, "$lt": 8000}})',
     db.videos.find({"category": "Наука", "views": {"$gte": 1500, "$lt": 8000}},
                    {"title": 1, "views": 1, "_id": 0}))

show('3. db.videos.find({"status": "published"}, projection).sort("views", -1).limit(5)',
     db.videos.find({"status": "published"}, {"title": 1, "views": 1, "_id": 0})
       .sort("views", DESCENDING).limit(5))

show('4. db.videos.find({"tags": "mongodb"}, {"title": 1, "tags": 1, "_id": 0})',
     db.videos.find({"tags": "mongodb"}, {"title": 1, "tags": 1, "_id": 0}))

show('5. db.users.find({"profile.country": "Россия", "interests": "Технологии"})',
     db.users.find({"profile.country": "Россия", "interests": "Технологии"},
                   {"username": 1, "profile": 1, "_id": 0}))

print('\n6. db.comments.insert_one({...})')
inserted_id = db.comments.insert_one({
    "videoId": db.videos.find_one({"title": "Индексы в MongoDB"})["_id"],
    "userId": db.users.find_one({"username": "user1"})["_id"],
    "text": "Демонстрационный комментарий",
    "createdAt": datetime.now(timezone.utc), "likes": 0,
}).inserted_id
pprint(db.comments.find_one({"_id": inserted_id}), sort_dicts=False)

print('\n7. db.comments.update_one({"_id": inserted_id}, {"$set": {"text": "Исправленный комментарий"}})')
db.comments.update_one({"_id": inserted_id},
                       {"$set": {"text": "Исправленный комментарий"}})
pprint(db.comments.find_one({"_id": inserted_id}), sort_dicts=False)

print('\n8. db.comments.delete_one({"_id": inserted_id})')
print("deleted_count:", db.comments.delete_one({"_id": inserted_id}).deleted_count)

invalid_user = {
    "username": "invalid_user", "joinedAt": datetime.now(timezone.utc),
    "profile": {"displayName": "Ошибка", "country": "Россия"},
}
print('\n9. db.users.insert_one(')
pprint(invalid_user, sort_dicts=False)
print(') — без обязательного email, ожидаемый отказ')
try:
    db.users.insert_one(invalid_user)
    raise AssertionError("Невалидный документ был сохранён")
except WriteError as error:
    print(f"MongoDB отклонила документ: code={error.code}, "
          f"message={(error.details or {}).get('errmsg')}")

client.close()
