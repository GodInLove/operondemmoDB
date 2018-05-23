# coding:utf8
from flask import Flask
from flask_mail import Mail

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'operondemmoDB',
    'host': 'localhost',
    'port': 27017,
}

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '1007383380@qq.com'
app.config['MAIL_PASSWORD'] = 'pavinxonzcpubdbf'
app.config["MAIL_SENDER"] = '1007383380@qq.com'
app.config['SECRET_KEY'] = "5c3dd5b15c704463af33cfa4141e6572"
app.debug = True
path = app.instance_path
process = 4
sender = app.config["MAIL_SENDER"]
mail = Mail(app)
self_link = "127.0.0.1:5000"
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")
