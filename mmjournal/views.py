'''
    Project: MyMusicianJournal
    Course: CISP 247 [Database Design]
    Professor: Samer Hanoudi
    Student: Chris Laponsie
    Date started: 8/25/2020
    Last updated: 8/25/2020

    A barebones flask app for helping beginner and advanced musicians track
    their progress while practicing.  Intented to show proficiency with 
    database design using SQLite.

'''

import flask

from datetime import datetime
import flask_login
from mmjournal import app
from mmjournal import login_manager
import mmjournal.db as mmjdb

# sha256 used for passwords
from passlib.hash import sha256_crypt

con = mmjdb.connect()
mmjdb.init_schema (con)
con.close()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    user_data = mmjdb.get_user_by_email(mmjdb.get_db(),email)
    if not user_data:
        return

    user = User()
    user.key = user_data[0]
    user.id = user_data[1]
    user.email = user_data[1]

    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    user_data = mmjdb.get_user_by_email(mmjdb.get_db(),email)
    if not user_data:
        return
    print (user_data)
    user = User()
    user.key = user_data[0]
    user.id = user_data[1]
    user.email = user_data[1]
    if (sha256_crypt.verify(request.form['password'], user_data[2])):
        return user
    else: return None
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')

    email = flask.request.form['email']
    user_data = mmjdb.get_user_by_email(mmjdb.get_db(),email)
    if not user_data:
        return flask.render_template('login.html', update_msg = 'Email not registered')
    if (sha256_crypt.verify(flask.request.form['password'], user_data[2])):
        user = User()
        user.key = user_data[0]
        user.id = user_data[1]
        user.email = user_data[1]
        flask_login.login_user(user)
        return flask.render_template('index.html', update_msg = 'Thank you for logging in.', user_id = flask_login.current_user.id)

    return flask.render_template('login.html', update_msg = 'Login Failed!')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.render_template('login.html', update_msg = 'You have been logged out.')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'GET':
        if (flask_login.current_user.is_authenticated):
            return flask.render_template('index.html', update_msg = 'You have already registered.')
        else:
            return flask.render_template('register.html')
    else:
        if (flask.request.form['password']==flask.request.form['password2']):
            db = mmjdb.get_db()

            passwd = sha256_crypt.hash(flask.request.form['password'])
            
            if mmjdb.create_user(db, [flask.request.form['email'],passwd]):
                return flask.render_template('register.html', success=True)
            else:
                return flask.render_template('register.html', fail=True)
        else:
            return flask.render_template('register.html', update_msg = 'Passwords didn\'t match')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.render_template('login.html', update_msg = 'You must be logged in to view this content.')



@app.route('/')
@flask_login.login_required
def index():
    recent = mmjdb.get_recent_sessions(mmjdb.get_db(), flask_login.current_user.key)
    print (recent)
    return flask.render_template('summary.html', recent_sessions = recent)


@app.route('/edit_categories', methods=['GET', 'POST'])

@flask_login.login_required
def categories():
    if flask.request.method == 'POST':
        category_name = flask.request.form['category_name']
        mmjdb.create_category (mmjdb.get_db(), [flask_login.current_user.key, category_name])
    category_list = mmjdb.get_categories_by_user_id(mmjdb.get_db(), flask_login.current_user.key)
    return flask.render_template('edit_categories.html', category_list = category_list)

@app.route('/edit_exercises', methods=['GET', 'POST'])
@flask_login.login_required
def edit_exercises():
    if flask.request.method == 'POST':
        category_id = flask.request.form['category_id']
        exercise_name = flask.request.form['name']
        source_url =  flask.request.form['source_url']
        notes =  flask.request.form['notes']
        uom =  flask.request.form['uom']
        mmjdb.create_exercise (mmjdb.get_db(),
            [flask_login.current_user.key, category_id, exercise_name, source_url, notes, uom])
    category_list = mmjdb.get_categories_by_user_id(mmjdb.get_db(), flask_login.current_user.key)
    exercise_list = mmjdb.get_exercises_by_user_id(mmjdb.get_db(), flask_login.current_user.key)
    print (exercise_list)
    return flask.render_template('edit_exercises.html', category_list = category_list, exercise_list = exercise_list)

@app.route('/practice')
@flask_login.login_required
def practice():
    choices = mmjdb.get_exercise_choices(mmjdb.get_db(), flask_login.current_user.key)
    return flask.render_template('practice.html', exercise_choices = choices)

@app.route('/log_practice', methods=['POST'])
@flask_login.login_required
def log_practice():
    print (flask.request.form)
    exercise_id = flask.request.form['exercise_id']
    start_time = flask.request.form['start_time']
    end_time = flask.request.form['end_time']
    achievement =  flask.request.form['achievement']
    user_id =  flask_login.current_user.key
    return_msg = 'Error logging practice session'
    
    if (mmjdb.log_practice_session(mmjdb.get_db(), [
        user_id, exercise_id, start_time, end_time, achievement
        ])):
        return_msg = 'Practice session logged'

    choices = mmjdb.get_exercise_choices(mmjdb.get_db(), flask_login.current_user.key)
    
    return flask.render_template('practice.html', exercise_choices = choices, update_msg = return_msg)

''' internal API calls... '''

@app.route('/api')
def api():
    args = flask.request.args
    output_dict = {}
    print (args)
    if 'action' in args:
        if args['action'] == 'get_exercise_details':
            exercise_id = args['id']
            values = mmjdb.get_exercise_details(mmjdb.get_db(), exercise_id)
            if (values):
                keys = ['exercise_id', 'user_id', 'category_id', 'name', 'source_url', 'notes', 'uom', 'category_name']
                output_dict = dict(zip(keys, values))          
        elif args['action'] == 'get_piechart_data':
            user_id = args['id']
            output_dict = mmjdb.get_pie_dict (mmjdb.get_db(), user_id)
    return flask.jsonify (output_dict)

app.add_url_rule('/', 'index', index)

if __name__ == '__main__':
    app.run(debug=True)