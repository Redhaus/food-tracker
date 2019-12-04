import sqlite3

from flask import g


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


# helps prevent memory leaks
# autoclose db connection after return
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
