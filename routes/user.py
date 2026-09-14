from flask import Blueprint, jsonify, render_template, session
from routes.auth_middleware import login_required

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.get("")
@user_bp.get("/")
def user_home():
    """用户端首页"""
    return render_template("user/index.html")

@user_bp.get("/products")
def user_products():
    """商品数据浏览页"""
    return render_template("user/products.html")

@user_bp.get("/analysis")
def user_analysis():
    """多维数据可视化看板"""
    return render_template("user/analysis.html")

@user_bp.get("/upload")
@login_required
def user_upload_page():
    """CSV 上传页面"""
    return render_template("user/upload.html")

@user_bp.get("/datasets")
@login_required
def user_datasets_page():
    """数据集管理与自定义分析页面"""
    return render_template("user/datasets.html")

@user_bp.get("/profile")
@login_required
def profile():
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "user_id": session.get("user_id"),
            "username": session.get("username"),
            "role": session.get("role")
        }
    }), 200
