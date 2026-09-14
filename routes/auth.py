from flask import Blueprint, request, session, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import SessionLocal
from database.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.get("/login")
def login_page():
    return render_template("login.html")

@auth_bp.get("/register")
def register_page():
    return render_template("register.html")

@auth_bp.post("/register")
def register():
    """用户注册接口"""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()

    # 1. 用户名格式检查
    if not username or len(username) < 3 or len(username) > 50:
        return jsonify({"code": 400, "message": "用户名长度需在 3 到 50 个字符之间", "data": None}), 400

    # 2. 密码长度检查
    if not password or len(password) < 6:
        return jsonify({"code": 400, "message": "密码长度不能少于 6 位", "data": None}), 400

    # 3. 两次密码一致性检查
    if password != confirm_password:
        return jsonify({"code": 400, "message": "两次输入的密码不一致", "data": None}), 400

    db = SessionLocal()
    try:
        # 4. 用户名唯一性检查
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({"code": 400, "message": "该用户名已被注册", "data": None}), 400

        # 5. 密码哈希存储
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            password_hash=password_hash,
            role="user",
            status=1
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return jsonify({
            "code": 200,
            "message": "注册成功",
            "data": {
                "id": new_user.id,
                "username": new_user.username,
                "role": new_user.role
            }
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({"code": 500, "message": f"注册失败：{str(e)}", "data": None}), 500
    finally:
        db.close()

@auth_bp.post("/login")
def login():
    """用户登录接口"""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"code": 400, "message": "请输入用户名和密码", "data": None}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"code": 400, "message": "用户名或密码错误", "data": None}), 400

        if user.status != 1:
            return jsonify({"code": 403, "message": "该账号已被禁用，请联系管理员", "data": None}), 403

        # 记录 session
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role

        return jsonify({
            "code": 200,
            "message": "登录成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "redirect_url": "/admin" if user.role == "admin" else "/"
            }
        }), 200
    finally:
        db.close()

@auth_bp.post("/logout")
def logout():
    """退出登录接口"""
    session.clear()
    return jsonify({
        "code": 200,
        "message": "已退出登录",
        "data": None
    }), 200

@auth_bp.get("/current_user")
def get_current_user():
    """获取当前登录用户信息"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "code": 200,
            "message": "未登录",
            "data": None
        }), 200

    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "id": user_id,
            "username": session.get("username"),
            "role": session.get("role")
        }
    }), 200
