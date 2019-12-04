from flask import Flask, render_template, g, request
from database import get_db, connect_db
# import datetime
from datetime import datetime

app = Flask(__name__)



# helps prevent memory leaks
# autoclose db connection after return of route
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# ROUTES
# HOME WHERE NEW DAYS AND FOODS CAN BE ADDED
@app.route('/', methods=['POST', 'GET'])
def home():
    db = get_db()

    # if post get date from form, confirm string to datetime obj
    # then format datetime obj into a string
    if request.method == 'POST':

        date = request.form['date']
        dt = datetime.strptime(date, '%Y-%m-%d')
        string_date = datetime.strftime(dt, '%Y%m%d')

        # insert it into the db and commit the save
        db.execute('insert into log_date (entry_date) values (?)', [string_date])
        db.commit()

    #  retrieve all log data based on date by joining tables
    cur = db.execute('select log_date.entry_date, '
                     'sum(food.protein) as protein, '
                     'sum(food.carbohydrates) as carb, '
                     'sum(food.fat) as fat, '
                     'sum(food.calories ) as cal '
                     'from log_date '
                     'inner join food_date '
                     'on food_date.log_date_id = log_date.id '
                     'join food '
                     'on food.id = food_date.food_id '
                     'group by log_date.id order by entry_date desc ')
    results = cur.fetchall()

    # create an empty array to store date objects
    date_results = []

    # loop through results of dates
    # create a single date dict for each add, nutrition data and date
    # get each date string and convert to a datetime object
    # format dt obj into a pretty version and add to single date object
    # append single date to date results array

    for i in results:
        single_date = {}
        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carb'] = i['carb']
        single_date['fat'] = i['fat']
        single_date['cal'] = i['cal']
        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
        single_date['pretty_date'] = datetime.strftime(d, '%B %d, %Y')
        date_results.append(single_date)

    return render_template('home.html', results=date_results)

# ADD FOOD
@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    # get all data from form and convert numbers into ints
    if request.method == 'POST':
        name = request.form['food_name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])

        # calculate the calories based on formula
        calories = protein * 4 + carbohydrates * 4 + fat * 9

        # insert them into database and commit
        db.execute('insert into food '
                   '(name, protein, carbohydrates, fat, calories ) '
                   'values (?,?,?,?,?)',
                   [name, protein, carbohydrates, fat, calories])
        db.commit()

    # get all food data in food table to display it on addition
    cur = db.execute('select * from food')
    results = cur.fetchall()

    return render_template('add_food.html', results=results)


# VIEW INDIVIDUAL DAY
@app.route('/view/<date>', methods=['GET', 'POST'])
def view(date):
    # get db connection
    db = get_db()

    # GET CURRENT DATE AND ID
    # get date from db that matches url date
    # getting the log_date
    cur = db.execute('select id, entry_date '
                     'from log_date '
                     'where entry_date = ?',
                     [date])
    date_result = cur.fetchone()


    # GRAB FORM DATA FOR FOOD from form & SAVE TO DB WITH DATE ID
    # if post method get food selected from form
    # get the dates id
    if request.method == 'POST':
        select = request.form['food-select']
        id = date_result['id']

        # save the date id and the food id to the food_date table
        # so you can display all food from a specific day
        db.execute('insert into food_date (food_id, log_date_id) '
                   'values (?,?)', [select, id])
        db.commit()


    # SQL QUERY TO JOIN ALL TABLES TO RETURN FOOD DATA FOR SPECIFIC DATE
    # joining all three tables
    # filtered by entry_date
    # selecting food info from that larger joined table
    log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories '
                         'from log_date '
                         'join food_date '
                         'on food_date.log_date_id = log_date.id '
                         'join food '
                         'on food.id = food_date.food_id '
                         'where log_date.entry_date = ?',
                         [date])

    food_list = log_cur.fetchall()


    # CREATE DICT FOR FOOD TOTALS
    # create dict with all totals for the day
    totals = {'protein': 0, 'carbohydrates': 0, 'fat': 0, 'calories': 0}

    # loop through food_list and assign values to dict
    for food in food_list:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']


    # parse that date into a datetime obj then format it to be pretty
    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')

    # get food id and name from db
    food_cur = db.execute('select id, name from food')
    food_results = food_cur.fetchall()


    # Pass data into template
    return render_template('day.html',
                           entry_date=date_result['entry_date'],
                           pretty_date=pretty_date,
                           food_results=food_results,
                           food_list=food_list,
                           totals=totals
                           )


# RUN APP CHECK
if __name__ == '__main__':
    app.run(debug=True)
