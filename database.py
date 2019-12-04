# DATABASE HELPERS
from flask import g
import sqlite3

# used by global_db
def connect_db():
    # connect to db at db location
    sql = sqlite3.connect('/Users/redbook/PycharmProjects/FoodTracker/food_log.db')
    # return querys as dictionaries rather than tuples
    sql.row_factory = sqlite3.Row
    return sql


# create a function that will get db anytime need it in app
def get_db():
    # if global attribute doesn't have sqlite3 then add it'
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
