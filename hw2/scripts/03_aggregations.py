"""Агрегация, $lookup и аналитика вовлечённости."""
from pprint import pprint

from common import connect


def run(label, collection, pipeline):
    print(f"\n{label}")
    print(f"db.{collection}.aggregate(")
    pprint(pipeline, sort_dicts=False, width=100)
    print(") ->")
    for document in db[collection].aggregate(pipeline):
        pprint(document, sort_dicts=False, width=100)


client, db = connect()

run("1. Количество видео и средние просмотры по категориям", "videos", [
    {"$match": {"status": "published"}},
    {"$group": {"_id": "$category", "videoCount": {"$sum": 1},
                "averageViews": {"$avg": "$views"}}},
    {"$sort": {"averageViews": -1}},
])

run("2. $lookup: видео, канал и владелец канала", "videos", [
    {"$match": {"category": "Технологии"}},
    {"$lookup": {"from": "channels", "localField": "channelId",
                 "foreignField": "_id", "as": "channel"}},
    {"$unwind": "$channel"},
    {"$lookup": {"from": "users", "localField": "channel.ownerId",
                 "foreignField": "_id", "as": "owner"}},
    {"$unwind": "$owner"},
    {"$project": {"_id": 0, "title": 1, "views": 1,
                  "channel": "$channel.name", "author": "$owner.profile.displayName"}},
    {"$sort": {"views": -1}},
])

run("3. Какие категории дают больше лайков на 1000 просмотров?", "videos", [
    {"$match": {"status": "published", "views": {"$gte": 1000}}},
    {"$project": {"category": 1, "views": 1, "likes": 1,
                  "likesPer1000": {"$multiply": [
                      {"$divide": ["$likes", "$views"]}, 1000]}}},
    {"$group": {"_id": "$category", "videoCount": {"$sum": 1},
                "totalViews": {"$sum": "$views"}, "totalLikes": {"$sum": "$likes"},
                "averageLikesPer1000": {"$avg": "$likesPer1000"}}},
    {"$sort": {"averageLikesPer1000": -1}},
    {"$limit": 4},
])

run("4. $unwind: наиболее частые теги", "videos", [
    {"$unwind": "$tags"},
    {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
    {"$sort": {"count": -1, "_id": 1}},
    {"$limit": 5},
])

client.close()
