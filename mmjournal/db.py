import sqlite3
import flask
from sqlite3 import Error
from mmjournal import app


# module constants
DB_PATH = 'mmj.db'
USER_TABLE = 'Users'
PRACTICE_SESSION_TABLE = 'PracticeSession'
EXERCISE_CATEGORIES_TABLE = 'ExerciseCategories'
EXERCISE_TABLE = 'Exercise'

def connect (path = DB_PATH):
    conn = sqlite3.connect(path, timeout=10)
    return conn

def init_schema (dbcon):
    ''' called when __name__ == __main__
    Doesn't get called when imported as a module
    Must run python db.py to init schema for this project

    creates the db and populates it with necessary tables/relationships
    '''
    print ('Initializing database schema')
    # these are reused between tables so storing them as strings to reduce typing.
    user_constraint = 'FOREIGN KEY (user_id) REFERENCES %s (user_id)' % USER_TABLE
    category_constraint = 'FOREIGN KEY (category_id) REFERENCES %s (category_id)' % EXERCISE_CATEGORIES_TABLE
    exercise_constraint = 'FOREIGN KEY (exercise_id) REFERENCES %s (exercise_id)' % EXERCISE_TABLE

    dbdict = {
        'user_id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'email_address': 'TEXT',
        'password': 'TEXT'
    }
    print ('Creating %s table' % USER_TABLE)
    create_table (dbcon, USER_TABLE, dbdict)

    dbdict = {
        'category_id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'user_id' : 'INTEGER',
        'category_name' : 'TEXT'
    }
    constraints = [user_constraint]
    print ('Creating %s table' % EXERCISE_CATEGORIES_TABLE)
    create_table (dbcon, EXERCISE_CATEGORIES_TABLE, dbdict, constraints)

    dbdict = {
        'exercise_id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'user_id' : 'INTEGER',
        'category_id' : 'INTEGER',
        'name' : 'TEXT',
        'source_url' : 'TEXT',
        'notes' : 'TEXT',
        'uom' : 'TEXT'
    }
    constraints = [user_constraint, category_constraint]
    print ('Creating %s table' % EXERCISE_TABLE)
    create_table (dbcon, EXERCISE_TABLE, dbdict, constraints)

    dbdict = {
        'session_id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'user_id' : 'INTEGER',
        'exercise_id' : 'INTEGER',
        'start_timestamp' : 'INTEGER',
        'end_timestamp' : 'INTEGER',
        'achievement' : 'REAL'
    }
    constraints = [user_constraint, exercise_constraint]
    print ('Creating %s table' % PRACTICE_SESSION_TABLE)
    create_table (dbcon, PRACTICE_SESSION_TABLE, dbdict, constraints)

    # create default user
    user = query_db(dbcon, 'select * from Users where user_id = 1',
                one=True)
    
    if user:
        print ('User defaults already populated')
    else:
        print ('Creating default user')
        create_user (dbcon, ['default', 'default'])
        create_category (dbcon, [1, 'Scale'])
        create_category (dbcon, [1, 'Chord Progression'])
        create_category (dbcon, [1, 'Improvisation'])
        create_category (dbcon, [1, 'Etude'])
        print ('done')

def create_table (dbcon, table_name, columns_dict, constraints = None):
    '''
    A requirement for CISP 247 is to discuss dynamic vs embedded SQL.
    While the specific SQL queries to create the tables and framework
    for this DB could be hard-coded, I decided to write a function to do this
    dynamically just to reduce copy/pasting of SQL syntax.
    Using an Object Relational Mapper (ORM) like SQLAlchemy results
    in fully wrapping the SQL language and interfacing with just the ORM,
    so SQL is fully dynamic.  In order to demonstrate proficiency though,
    I decided *not* to use SQLAlchemy.

    columns is a dict containing the columns and associated types/constraints.
    table_name is name of the table.
    constraints is a list of strings defining sqlite relationships
    '''
     
    column_definitions = ', '.join(['%s %s' % (x,y) for x, y in columns_dict.items()])
    
    if constraints:
        constraints_sql = ', '.join(constraints)
        column_definitions = '%s, %s' % (column_definitions, constraints_sql)
    table_sql =  'CREATE TABLE IF NOT EXISTS %s(%s);' % (table_name, column_definitions)
    try_sql (dbcon, table_sql)

def try_sql (dbcon, sql):
    try:
        c = dbcon.cursor()
        c.execute(sql)
        return True
    except Error as e:
        print ('SQL ERROR')
        print (e)
        print ('SQL = %s' %sql)
        return False


def try_query (dbcon, sql):
    try:
        c = dbcon.cursor()
        c.execute(sql)
        rows = c.fetchall()
        c.close()
        return rows
    except Error as e:
        print ('SQL ERROR')
        print (e)
        print ('SQL = %s' %sql)
        return False

def query_db(dbcon, sql, args=(), one=False):
    c = dbcon.cursor()
    c.execute(sql, args)
    rv = c.fetchall()
    c.close()
    
    return (rv[0] if rv else None) if one else rv

def get_user_by_email (conn, email):
    return query_db(conn, 'select * from Users where email_address = ?', args=[email],
                one=True)
                
def create_user(conn, user):
    sql = ''' INSERT INTO %s(email_address, password)
              VALUES(?,?) ''' % USER_TABLE
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid

def create_category(conn, category):
    sql = ''' INSERT INTO %s(user_id, category_name)
              VALUES(?,?) ''' % EXERCISE_CATEGORIES_TABLE
    cur = conn.cursor()
    cur.execute(sql, category)
    conn.commit()
    return cur.lastrowid


def create_exercise(conn, exercise):
    sql = ''' INSERT INTO %s(user_id, category_id, name, source_url, notes, uom)
              VALUES(?,?,?,?,?,?) ''' % EXERCISE_TABLE
    cur = conn.cursor()
    cur.execute(sql, exercise)
    conn.commit()
    return cur.lastrowid

def get_db():
    d = getattr(flask.g, '_database', None)
    if d is None:
        d = flask.g._database = sqlite3.connect(DB_PATH)
    return d

def get_categories (conn):
    return query_db(conn, 'select * from %s' % EXERCISE_CATEGORIES_TABLE)

def get_categories_by_user_id (conn, user_id):
    return query_db(conn, 'select * from %s where user_id = ? or user_id = 1' % EXERCISE_CATEGORIES_TABLE, args=[user_id])

def get_exercise_choices (conn, user_id):
    return query_db(conn, '''SELECT
                                exercise_id,
                                user_id,
                                name
                            FROM Exercise 
                            WHERE user_id = ? or user_id = 1''', args=[user_id])

def get_exercises_by_user_id (conn, user_id):
    # also fetches category name from ExerciseCategories using JOIN
    return query_db(conn, '''SELECT
                                exercise_id,
                                Exercise.user_id,
                                Exercise.category_id, 
                                Exercise.name, 
                                Exercise.source_url, 
                                Exercise.notes, 
                                Exercise.uom, 
                                ExerciseCategories.category_name
                            FROM Exercise 
                            INNER JOIN ExerciseCategories
                                ON ExerciseCategories.category_id = Exercise.category_id
                            WHERE Exercise.user_id = ? or Exercise.user_id = 1''', args=[user_id])

def get_exercise_details (conn, exercise_id):
    return query_db(conn, '''SELECT
                                exercise_id,
                                Exercise.user_id,
                                Exercise.category_id, 
                                Exercise.name, 
                                Exercise.source_url, 
                                Exercise.notes, 
                                Exercise.uom, 
                                ExerciseCategories.category_name
                            FROM Exercise 
                            INNER JOIN ExerciseCategories
                                ON ExerciseCategories.category_id = Exercise.category_id
                            WHERE exercise_id = ?''', args=[exercise_id],one=True)


def get_pie_dict (conn, user_id):
    sessions = get_recent_sessions (conn, user_id)
    pie_data = {}
    labels = []
    for _, _, _, _, _, _, _, _, cat, dur in sessions:
        if not (cat in pie_data):
            pie_data[cat] = 0
            labels.append (cat)
        pie_data[cat] += dur
    data = []
    for n in pie_data:
        data.append (pie_data[n])
    return {
        'labels': labels,
        'datasets': [{
            'label': 'Focus Categories',
            'backgroundColor': '#4e4caf',
            'data': data,
        }]
    }

def get_recent_sessions (conn, user_id):
    return query_db(conn, '''SELECT
                                PracticeSession.session_id,
                                PracticeSession.user_id,
                                PracticeSession.exercise_id,
                                PracticeSession.start_timestamp, 
                                PracticeSession.end_timestamp, 
                                PracticeSession.achievement,
                                Exercise.uom,
                                Exercise.name,
                                ExerciseCategories.category_name,
                                strftime('%s',PracticeSession.end_timestamp) - strftime('%s',PracticeSession.start_timestamp) as duration
                            FROM PracticeSession 
                            INNER JOIN Exercise
                                ON Exercise.exercise_id = PracticeSession.exercise_id
                            INNER JOIN ExerciseCategories
                                ON ExerciseCategories.category_id = Exercise.category_id
                            ''')

def log_practice_session (conn, session_data):
    sql = ''' INSERT INTO %s(user_id, exercise_id, start_timestamp, end_timestamp, achievement)
              VALUES(?,?,?,?,?) ''' % PRACTICE_SESSION_TABLE
    cur = conn.cursor()
    cur.execute(sql, session_data)
    conn.commit()
    return cur.lastrowid
@app.teardown_appcontext
def close_connection(exception):
    d = getattr(flask.g, '_database', None)
    if d is not None:
        d.close()


    