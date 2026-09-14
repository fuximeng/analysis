import os
from pathlib import Path
import pandas as pd
from flask import Blueprint, jsonify, render_template, request, session
from database.db import SessionLocal
from database.models import User, Product, CrawlTask, OperationLog
from routes.auth_middleware import admin_required
from analysis.data_clean import clean_data
from database.insert_products import insert_products

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------- 页面渲染路由 -----------------

@admin_bp.get("")
@admin_bp.get("/")
@admin_required
def admin_home():
    """管理后台控制台概览"""
    return render_template("admin/index.html")

@admin_bp.get("/crawler")
@admin_required
def admin_crawler_page():
    """数据采集管理页"""
    return render_template("admin/crawler.html")

@admin_bp.get("/data")
@admin_required
def admin_data_page():
    """数据清洗与质量管理页"""
    return render_template("admin/data.html")

@admin_bp.get("/analysis")
@admin_required
def admin_analysis_page():
    """系统全量数据分析洞察页"""
    return render_template("admin/analysis.html")

@admin_bp.get("/users/page")
@admin_bp.get("/users-view")
@admin_required
def admin_users_page():
    """用户权限管理页（兼容别名）"""
    return render_template("admin/users.html")

@admin_bp.get("/logs")
@admin_required
def admin_logs_page():
    """运行与操作日志页"""
    return render_template("admin/logs.html")


# ----------------- 管理后台 API 接口 -----------------

@admin_bp.get("/stats")
@admin_required
def admin_stats():
    """管理看板核心统计指标"""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        product_count = db.query(Product).count()
        task_count = db.query(CrawlTask).count()

        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "user_count": user_count,
                "product_count": product_count,
                "task_count": task_count
            }
        }), 200
    finally:
        db.close()


@admin_bp.get("/users")
@admin_required
def list_users():
    """获取所有用户列表（含普通用户与管理员）"""
    if "text/html" in request.headers.get("Accept", "") and not request.path.endswith(".json"):
        return render_template("admin/users.html")

    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.id.asc()).all()
        result = []
        for u in users:
            result.append({
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "status": u.status,
                "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else None
            })
        return jsonify({
            "code": 200,
            "message": "success",
            "data": result
        }), 200
    finally:
        db.close()


@admin_bp.post("/users/<int:user_id>/status")
@admin_required
def update_user_status(user_id):
    """切换用户账号状态（启用 1 / 禁用 0）"""
    data = request.get_json() or {}
    status = data.get("status")
    if status not in (0, 1):
        return jsonify({"code": 400, "message": "状态参数不合法", "data": None}), 400

    db = SessionLocal()
    try:
        target_user = db.query(User).filter_by(id=user_id).first()
        if not target_user:
            return jsonify({"code": 404, "message": "用户不存在", "data": None}), 404

        if target_user.id == session.get("user_id"):
            return jsonify({"code": 400, "message": "不能修改当前登录账号自身的状态", "data": None}), 400

        target_user.status = status
        log = OperationLog(
            user_id=session.get("user_id"),
            operation="update_user_status",
            target=f"user_{user_id}",
            detail=f"更新用户 {target_user.username} 状态为 {'启用' if status == 1 else '禁用'}"
        )
        db.add(log)
        db.commit()

        return jsonify({
            "code": 200,
            "message": f"用户状态已{'启用' if status == 1 else '禁用'}",
            "data": {"user_id": user_id, "status": status}
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({"code": 500, "message": str(e), "data": None}), 500
    finally:
        db.close()


@admin_bp.get("/quality-check")
@admin_required
def admin_quality_check():
    """数据质量检查接口"""
    raw_csv = BASE_DIR / "data" / "raw" / "products_raw.csv"
    if not raw_csv.exists():
        raw_csv = BASE_DIR / "data" / "raw" / "dummyjson_products.csv"

    if not raw_csv.exists():
        return jsonify({"code": 404, "message": "原始数据文件不存在", "data": None}), 404

    df = pd.read_csv(raw_csv)
    id_col = "product_id" if "product_id" in df else "id"
    duplicate_count = int(df[id_col].duplicated().sum()) if id_col in df else 0
    invalid_price = int((df["price"] <= 0).sum()) if "price" in df else 0
    invalid_rating = int(((df["rating"] < 0) | (df["rating"] > 5)).sum()) if "rating" in df else 0
    brand_missing = int(df["brand"].isnull().sum()) if "brand" in df else 0

    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "row_count": len(df),
            "duplicate_count": duplicate_count,
            "invalid_price_count": invalid_price,
            "invalid_rating_count": invalid_rating,
            "brand_missing_count": brand_missing
        }
    }), 200


@admin_bp.post("/clean-sync")
@admin_required
def admin_clean_and_sync():
    """触发清洗并将清洗后的数据入库"""
    raw_csv = BASE_DIR / "data" / "raw" / "products_raw.csv"
    if not raw_csv.exists():
        raw_csv = BASE_DIR / "data" / "raw" / "dummyjson_products.csv"

    if not raw_csv.exists():
        return jsonify({"code": 404, "message": "原始数据文件不存在", "data": None}), 404

    try:
        raw_df = pd.read_csv(raw_csv)
        cleaned_df = clean_data(raw_df)
        insert_products()

        db = SessionLocal()
        total_p = db.query(Product).count()
        op = OperationLog(
            user_id=session.get("user_id"),
            operation="clean_and_sync_products",
            target="products",
            detail=f"清洗原始数据并同步入库，当前全库商品总数: {total_p}"
        )
        db.add(op)
        db.commit()
        db.close()

        return jsonify({
            "code": 200,
            "message": "数据清洗并入库成功",
            "data": {
                "cleaned_rows": len(cleaned_df),
                "total_products": total_p
            }
        }), 200
    except Exception as e:
        return jsonify({"code": 500, "message": f"清洗同步失败: {str(e)}", "data": None}), 500


@admin_bp.get("/crawler-log")
@admin_required
def get_crawler_log():
    """读取爬虫最新运行日志内容"""
    log_path = BASE_DIR / "logs" / "crawler.log"
    if not log_path.exists():
        return jsonify({
            "code": 200,
            "message": "success",
            "data": {"content": "暂无日志文件"}
        }), 200

    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        recent_lines = lines[-100:] if len(lines) > 100 else lines
        return jsonify({
            "code": 200,
            "message": "success",
            "data": {"content": "".join(recent_lines)}
        }), 200
    except Exception as e:
        return jsonify({"code": 500, "message": f"读取日志出错: {str(e)}", "data": None}), 500
