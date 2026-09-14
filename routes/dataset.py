import json
from pathlib import Path
import pandas as pd
from flask import Blueprint, jsonify, session

from database.db import SessionLocal
from database.models import UserDataset, AnalysisRecord
from routes.auth_middleware import login_required
from analysis.custom_analysis import analyze_custom_dataset

dataset_bp = Blueprint("dataset", __name__, url_prefix="/dataset")

@dataset_bp.get("/list")
@login_required
def list_user_datasets():
    """获取当前登录用户的所有数据集列表"""
    user_id = session.get("user_id")
    role = session.get("role")

    db = SessionLocal()
    try:
        query = db.query(UserDataset)
        # 普通用户只看自己的数据集，管理员可看全部
        if role != "admin":
            query = query.filter_by(user_id=user_id)
        datasets = query.order_by(UserDataset.id.desc()).all()

        result = []
        for d in datasets:
            result.append({
                "id": d.id,
                "dataset_name": d.dataset_name,
                "file_name": d.file_name,
                "row_count": d.row_count,
                "status": d.status,
                "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else None
            })
        return jsonify({
            "code": 200,
            "message": "success",
            "data": result
        }), 200
    finally:
        db.close()


@dataset_bp.get("/<int:dataset_id>/analysis")
@login_required
def get_dataset_analysis(dataset_id):
    """获取指定数据集的分析结果，若无记录则即时重新计算"""
    user_id = session.get("user_id")
    role = session.get("role")

    db = SessionLocal()
    try:
        ds = db.query(UserDataset).filter_by(id=dataset_id).first()
        if not ds:
            return jsonify({"code": 404, "message": "数据集不存在", "data": None}), 404

        if role != "admin" and ds.user_id != user_id:
            return jsonify({"code": 403, "message": "无权访问此数据集", "data": None}), 403

        # 先查缓存的分析记录
        record = db.query(AnalysisRecord).filter_by(dataset_id=dataset_id).order_by(AnalysisRecord.id.desc()).first()
        if record and record.result_summary:
            try:
                data = json.loads(record.result_summary)
                return jsonify({
                    "code": 200,
                    "message": "success",
                    "data": data
                }), 200
            except Exception:
                pass

        # 若无分析记录或解析失败，尝试从文件动态生成
        file_p = Path(ds.file_path)
        if not file_p.exists():
            return jsonify({"code": 404, "message": "原始数据集文件已丢失", "data": None}), 404

        try:
            df = pd.read_csv(file_p)
        except Exception:
            df = pd.read_csv(file_p, encoding="gbk")

        analysis_res = analyze_custom_dataset(df)

        # 补录分析记录
        new_rec = AnalysisRecord(
            user_id=ds.user_id,
            dataset_id=ds.id,
            analysis_type="custom_dataset_analysis",
            result_summary=json.dumps(analysis_res, ensure_ascii=False)
        )
        db.add(new_rec)
        db.commit()

        return jsonify({
            "code": 200,
            "message": "success",
            "data": analysis_res
        }), 200
    finally:
        db.close()
