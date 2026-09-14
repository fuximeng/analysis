from functools import wraps
from flask import session, jsonify, request, redirect, url_for

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            if "text/html" in request.headers.get("Accept", "") and not request.path.startswith("/api/"):
                return redirect("/login")
            return jsonify({
                "code": 401,
                "message": "请先登录系统",
                "data": None
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            if "text/html" in request.headers.get("Accept", "") and not request.path.startswith("/api/"):
                return redirect("/login")
            return jsonify({
                "code": 401,
                "message": "请先登录系统",
                "data": None
            }), 401
        if session.get("role") != "admin":
            if "text/html" in request.headers.get("Accept", "") and not request.path.startswith("/api/"):
                return redirect("/")
            return jsonify({
                "code": 403,
                "message": "权限不足：需要管理员权限",
                "data": None
            }), 403
        return f(*args, **kwargs)
    return decorated_function
