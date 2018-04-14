# coding:utf8
from flask import Flask

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'operondemmoDB',
    'host': 'localhost',
    'port': 27017,
}
app.config['SECRET_KEY'] = "5c3dd5b15c704463af33cfa4141e6572"
app.debug = True
path = app.instance_path
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")
