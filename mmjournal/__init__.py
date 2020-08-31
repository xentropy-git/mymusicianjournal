import flask
import flask_login

app = flask.Flask(__name__)
app.secret_key = b'CISP247'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)



import mmjournal.views

