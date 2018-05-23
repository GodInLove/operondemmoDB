# coding:utf8
from app import app
from werkzeug.security import check_password_hash,generate_password_hash
from app.model import Admin
if __name__ == '__main__':
    new_admin = Admin(email="123@qq.com",admin_id="admin",password=generate_password_hash(("123456")))
    new_admin.save()
    app.run()
