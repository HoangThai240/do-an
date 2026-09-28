from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from dotenv import load_dotenv
import os


# ==========================================
# ĐỌC FILE .ENV
# ==========================================

load_dotenv()


# ==========================================
# KHỞI TẠO FLASK APP
# ==========================================

app = Flask(__name__)


# ==========================================
# CẤU HÌNH SECRET KEY
# ==========================================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "DO_AN_NGANH_NCKH_2026"
)


# ==========================================
# CẤU HÌNH DATABASE MYSQL
# ==========================================

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:1234@localhost/doannganhdb?charset=utf8mb4"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ==========================================
# CẤU HÌNH GMAIL
# ==========================================

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")


# ==========================================
# KHỞI TẠO DATABASE
# ==========================================

db = SQLAlchemy(app)


# ==========================================
# FLASK LOGIN
# ==========================================

login = LoginManager(app)


# ==========================================
# ENDPOINT ĐĂNG NHẬP
# ==========================================

login.login_view = "login_process"


# ==========================================
# THÔNG BÁO KHI CHƯA ĐĂNG NHẬP
# ==========================================

login.login_message = "Vui lòng đăng nhập để tiếp tục."

login.login_message_category = "warning"