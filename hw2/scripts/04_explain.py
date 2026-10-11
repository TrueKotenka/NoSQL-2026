"""Сравнение плана запроса до и после создания составного индекса."""
from pprint import pprint

from pymongo import ASCENDING, DESCENDING

from common import connect


def explain(hint=None):
    find_command = {"find": "videos", "filter": {"category": "Технологии"},
                    "sort": {"views": -1}}
    if hint is not None:
        find_command["hint"] = hint
    return db.command({"explain": find_command, "verbosity": "executionStats"})


def summarize(label, result):
    stats = result["executionStats"]
    print(label)
    pprint({"nReturned": stats["nReturned"],
            "totalDocsExamined": stats["totalDocsExamined"],
            "totalKeysExamined": stats["totalKeysExamined"],
            "winningPlan": result["queryPlanner"]["winningPlan"]},
           sort_dicts=False, depth=5, width=100)


client, db = connect()
index_name = "category_views_idx"
if index_name in db.videos.index_information():
    db.videos.drop_index(index_name)

print('db.command({"explain": {"find": "videos", "filter": {"category": "Технологии"}, '
      '"sort": {"views": -1}}, "verbosity": "executionStats"})')
summarize("До создания индекса:", explain())

db.videos.create_index([("category", ASCENDING), ("views", DESCENDING)],
                       name=index_name)
print('\ndb.command({"explain": {"find": "videos", "filter": {"category": "Технологии"}, '
      '"sort": {"views": -1}, "hint": "category_views_idx"}, '
      '"verbosity": "executionStats"})')
summarize("После создания индекса:", explain(index_name))
print("hint фиксирует индексный план на маленькой учебной выборке.")
client.close()
