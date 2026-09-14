import os
import json
from pathlib import Path
import pandas as pd
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename

from database.db import SessionLocal
from database.models import UserDataset, AnalysisRecord, OperationLog
from routes.auth_middleware import login_required
from analysis.custom_analysis import analyze_custom_dataset

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / "data" / "user_upload"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# 允许的扩展名与大小限制 (100MB)
ALLOWED_EXTENSIONS = {"csv"}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.post("")
@upload_bp.post("/")
@login_required
def upload_csv():
    """
    处理用户上传 CSV 文件：格式检查、大小检查、存储、创建数据集记录、生成自动化分析
    """
    user_id = session.get("user_id")
    if "file" not in request.files:
        return jsonify({"code": 400, "message": "请上传 CSV 文件", "data": None}), 400

    file = request.files["file"]
    dataset_name = request.form.get("dataset_name", "").strip() or "未命名数据集"

    if file.filename == "":
        return jsonify({"code": 400, "message": "未选择有效文件", "data": None}), 400

    if not allowed_file(file.filename):
        return jsonify({"code": 400, "message": "只支持上传 .csv 文件", "data": None}), 400

    # 安全文件名保存
    safe_name = secure_filename(file.filename) or "dataset.csv"
    save_filename = f"user_{user_id}_{int(pd.Timestamp.now().timestamp())}_{safe_name}"
    save_path = UPLOAD_FOLDER / save_filename

    try:
        file.save(str(save_path))
        # 检查文件大小
        if save_path.stat().st_size > MAX_CONTENT_LENGTH:
            save_path.unlink(missing_ok=True)
            return jsonify({"code": 400, "message": "文件大小超出 100MB 限制", "data": None}), 400

        # 读取并解析 CSV 数据
        try:
            df = pd.read_csv(save_path)
        except Exception:
            # 兼容 gbk 编码
            try:
                df = pd.read_csv(save_path, encoding="gbk")
            except Exception as e:
                save_path.unlink(missing_ok=True)
                return jsonify({"code": 400, "message": f"CSV 文件解析失败: {str(e)}", "data": None}), 400

        if df.empty:
            save_path.unlink(missing_ok=True)
            return jsonify({"code": 400, "message": "CSV 文件内容为空", "data": None}), 400

        row_count = len(df)

        # 执行自动化自定义分析
        analysis_res = analyze_custom_dataset(df)

        # 写入数据库 user_datasets 表与 analysis_records 表
        db = SessionLocal()
        try:
            new_dataset = UserDataset(
                user_id=user_id,
                dataset_name=dataset_name,
                file_name=file.filename,
                file_path=str(save_path),
                row_count=row_count,
                status="ready"
            )
            db.add(new_dataset)
            db.commit()
            db.refresh(new_dataset)

            # 保存分析记录
            new_record = AnalysisRecord(
                user_id=user_id,
                dataset_id=new_dataset.id,
                analysis_type="custom_dataset_analysis",
                result_summary=json.dumps(analysis_res, ensure_ascii=False)
            )
            db.add(new_record)

            # 记录操作日志
            op = OperationLog(
                user_id=user_id,
                operation="upload_csv_dataset",
                target=f"dataset_{new_dataset.id}",
                detail=f"用户上传数据集: {dataset_name}, 行数: {row_count}"
            )
            db.add(op)
            db.commit()

            return jsonify({
                "code": 200,
                "message": "CSV 数据集上传并分析成功",
                "data": {
                    "id": new_dataset.id,
                    "dataset_name": new_dataset.dataset_name,
                    "row_count": new_dataset.row_count,
                    "columns": analysis_res.get("columns", [])
                }
            }), 200
        except Exception as e:
            db.rollback()
            return jsonify({"code": 500, "message": f"入库失败: {str(e)}", "data": None}), 500
        finally:
            db.close()

    except Exception as e:
        return jsonify({"code": 500, "message": f"文件保存异常: {str(e)}", "data": None}), 500
