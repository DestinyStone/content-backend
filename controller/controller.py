# 创建联系人 - POST
import jwt
from flask import Blueprint, request, jsonify, send_file
from sqlalchemy import or_
import pandas as pd
import io
from werkzeug.utils import secure_filename
import os

from models.model import Contact, db, User

controller = Blueprint('controller', __name__)
app = controller


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400

    hashed_password = data['password']
    new_user = User(
        username=data['username'],
        password=hashed_password,
        nickname=data['nickname'],
        realname=data['realname']
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '用户注册成功'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and user.password == data['password']:
        return jsonify({
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'realname': user.realname
            }
        }), 200

    return jsonify({'message': '用户名或密码错误'}), 401

@app.route('/api/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    data = request.get_json()
    user.nickname = data.get('nickname', user.nickname)
    user.realname = data.get('realname', user.realname)

    if 'password' in data and data['password']:
        user.password = data['password']

    db.session.commit()

    return jsonify({'message': '个人信息更新成功'}), 200

# 联系人路由
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    # 支持查询参数：bookmarked（只获取书签联系人）、search（搜索）
    bookmarked_only = request.args.get('bookmarked', 'false').lower() == 'true'
    search_query = request.args.get('search', '').strip()
    
    query = Contact.query
    
    if bookmarked_only:
        query = query.filter_by(is_bookmarked=True)
    
    if search_query:
        query = query.filter(
            or_(
                Contact.name.contains(search_query),
                Contact.phone.contains(search_query),
                Contact.email.contains(search_query)
            )
        )
    
    contacts = query.all()
    return jsonify([{
        'id': contact.id,
        'name': contact.name,
        'phone': contact.phone,
        'email': contact.email,
        'gender': contact.gender,
        'age': contact.age,
        'is_bookmarked': contact.is_bookmarked,
        'social_media': contact.social_media or '',
        'address': contact.address or '',
        'additional_phone': contact.additional_phone or '',
        'notes': contact.notes or ''
    } for contact in contacts])

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    data = request.get_json()
    new_contact = Contact(
        name=data['name'],

        phone=data['phone'],
        email=data['email'],
        gender=data['gender'],
        age=data['age'],
        is_bookmarked=data.get('is_bookmarked', False),
        social_media=data.get('social_media', ''),
        address=data.get('address', ''),
        additional_phone=data.get('additional_phone', ''),
        notes=data.get('notes', '')
    )

    db.session.add(new_contact)
    db.session.commit()

    return jsonify({'message': '联系人添加成功'}), 201

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    contact = Contact.query.get(contact_id)
    if not contact:
        return jsonify({'message': '联系人不存在'}), 404

    data = request.get_json()
    contact.name = data.get('name', contact.name)
    contact.phone = data.get('phone', contact.phone)
    contact.email = data.get('email', contact.email)
    contact.gender = data.get('gender', contact.gender)
    contact.age = data.get('age', contact.age)
    contact.is_bookmarked = data.get('is_bookmarked', contact.is_bookmarked)
    contact.social_media = data.get('social_media', contact.social_media)
    contact.address = data.get('address', contact.address)
    contact.additional_phone = data.get('additional_phone', contact.additional_phone)
    contact.notes = data.get('notes', contact.notes)

    db.session.commit()

    return jsonify({'message': '联系人更新成功'}), 200

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    contact = Contact.query.get(contact_id)
    if not contact:
        return jsonify({'message': '联系人不存在'}), 404

    db.session.delete(contact)
    db.session.commit()

    return jsonify({'message': '联系人删除成功'}), 200

@app.route('/api/contacts/<int:contact_id>/bookmark', methods=['PUT'])
def toggle_bookmark(contact_id):
    contact = Contact.query.get(contact_id)
    if not contact:
        return jsonify({'message': '联系人不存在'}), 404

    data = request.get_json()
    contact.is_bookmarked = data.get('is_bookmarked', not contact.is_bookmarked)
    db.session.commit()

    return jsonify({
        'message': '书签状态更新成功',
        'is_bookmarked': contact.is_bookmarked
    }), 200

# Excel导出功能
@app.route('/api/contacts/export', methods=['GET'])
def export_contacts():
    contacts = Contact.query.all()
    
    # 创建DataFrame
    data = []
    for contact in contacts:
        data.append({
            '姓名': contact.name,
            '电话': contact.phone,
            '备用电话': contact.additional_phone or '',
            '邮箱': contact.email,
            '性别': contact.gender,
            '年龄': contact.age,
            '社交媒体': contact.social_media or '',
            '地址': contact.address or '',
            '备注': contact.notes or '',
            '书签': '是' if contact.is_bookmarked else '否'
        })
    
    df = pd.DataFrame(data)
    
    # 创建Excel文件在内存中
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='联系人')
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='联系人列表.xlsx'
    )

# Excel导入功能
@app.route('/api/contacts/import', methods=['POST'])
def import_contacts():
    if 'file' not in request.files:
        return jsonify({'message': '未选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': '未选择文件'}), 400
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 映射列名（支持中英文列名）
        column_mapping = {
            '姓名': 'name', 'name': 'name', 'Name': 'name',
            '电话': 'phone', 'phone': 'phone', 'Phone': 'phone',
            '备用电话': 'additional_phone', 'additional_phone': 'additional_phone',
            '邮箱': 'email', 'email': 'email', 'Email': 'email',
            '性别': 'gender', 'gender': 'gender', 'Gender': 'gender',
            '年龄': 'age', 'age': 'age', 'Age': 'age',
            '社交媒体': 'social_media', 'social_media': 'social_media',
            '地址': 'address', 'address': 'address', 'Address': 'address',
            '备注': 'notes', 'notes': 'notes', 'Notes': 'notes',
            '书签': 'is_bookmarked', 'is_bookmarked': 'is_bookmarked'
        }
        
        # 标准化列名
        df.columns = [column_mapping.get(col, col) for col in df.columns]
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 检查必填字段
                if pd.isna(row.get('name')) or pd.isna(row.get('phone')) or pd.isna(row.get('email')):
                    errors.append(f'第{index+2}行：缺少必填字段（姓名、电话、邮箱）')
                    continue
                
                # 处理书签字段
                is_bookmarked = False
                if 'is_bookmarked' in row:
                    bookmark_val = row['is_bookmarked']
                    if isinstance(bookmark_val, str):
                        is_bookmarked = bookmark_val in ['是', 'Yes', 'yes', 'True', 'true', '1']
                    else:
                        is_bookmarked = bool(bookmark_val)
                
                new_contact = Contact(
                    name=str(row['name']),
                    phone=str(row['phone']),
                    email=str(row['email']),
                    gender=str(row.get('gender', '未知')),
                    age=int(row.get('age', 0)) if not pd.isna(row.get('age')) else 0,
                    is_bookmarked=is_bookmarked,
                    social_media=str(row.get('social_media', '')) if not pd.isna(row.get('social_media')) else '',
                    address=str(row.get('address', '')) if not pd.isna(row.get('address')) else '',
                    additional_phone=str(row.get('additional_phone', '')) if not pd.isna(row.get('additional_phone')) else '',
                    notes=str(row.get('notes', '')) if not pd.isna(row.get('notes')) else ''
                )
                
                db.session.add(new_contact)
                imported_count += 1
            except Exception as e:
                errors.append(f'第{index+2}行：{str(e)}')
        
        db.session.commit()
        
        message = f'成功导入{imported_count}条联系人'
        if errors:
            message += f'，{len(errors)}条记录导入失败'
        
        return jsonify({
            'message': message,
            'imported_count': imported_count,
            'errors': errors
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'导入失败：{str(e)}'}), 500
