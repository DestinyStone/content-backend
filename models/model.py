import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nickname = db.Column(db.String(80), nullable=False)
    realname = db.Column(db.String(80), nullable=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # 书签字段：标记重要联系人
    is_bookmarked = db.Column(db.Boolean, default=False, nullable=False)
    # 多种联系方式
    social_media = db.Column(db.String(200), nullable=True)  # 社交媒体账号
    address = db.Column(db.String(200), nullable=True)  # 地址
    additional_phone = db.Column(db.String(20), nullable=True)  # 备用电话
    notes = db.Column(db.Text, nullable=True)  # 备注信息
