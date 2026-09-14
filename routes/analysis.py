from pathlib import Path
import pandas as pd
from flask import Blueprint, jsonify
from analysis.load_data import load_products
from analysis.basic_analysis import calculate_basic_statistics
from analysis.category_analysis import analyze_categories
from analysis.price_analysis import analyze_price
from analysis.rating_analysis import analyze_rating
from analysis.product_analysis import get_top_products

import time

analysis_bp = Blueprint("analysis", __name__, url_prefix="/analysis")
BASE_DIR = Path(__file__).resolve().parent.parent

_CACHE = {
    "df": None,
    "timestamp": 0
}
CACHE_TTL = 60  # 秒

def _get_analysis_df():
    now = time.time()
    if _CACHE["df"] is not None and (now - _CACHE["timestamp"] < CACHE_TTL):
        return _CACHE["df"]

    df = pd.DataFrame()
    try:
        df = load_products()
    except Exception:
        pass

    if df.empty:
        csv_paths = [
            BASE_DIR / "data" / "cleaned" / "products_cleaned.csv",
            BASE_DIR / "data" / "raw" / "products_raw.csv",
            BASE_DIR / "data" / "raw" / "dummyjson_products.csv"
        ]
        for path in csv_paths:
            if path.exists():
                try:
                    df = pd.read_csv(path)
                    if not df.empty:
                        break
                except Exception:
                    continue

    if not df.empty:
        _CACHE["df"] = df
        _CACHE["timestamp"] = now

    return df

@analysis_bp.get("/overview")
def get_overview():
    df = _get_analysis_df()
    if df.empty:
        return jsonify({"code": 200, "message": "暂无数据", "data": {}}), 200

    basic = calculate_basic_statistics(df)
    return jsonify({
        "code": 200,
        "message": "success",
        "data": basic
    }), 200

@analysis_bp.get("/category")
def get_category_analysis():
    df = _get_analysis_df()
    if df.empty:
        return jsonify({"code": 200, "message": "暂无数据", "data": []}), 200

    cat_df = analyze_categories(df).reset_index()
    records = cat_df.to_dict(orient="records")
    for r in records:
        # 兼容不同前端命名的别名 (count / product_count, average_price / avg_price)
        count_val = int(r.get("count", 0))
        avg_p = round(float(r.get("average_price", 0.0)), 2)
        avg_r = round(float(r.get("average_rating", 0.0)), 2)
        stock_val = int(r.get("total_stock", 0))

        r["count"] = count_val
        r["product_count"] = count_val
        r["average_price"] = avg_p
        r["avg_price"] = avg_p
        r["average_rating"] = avg_r
        r["total_stock"] = stock_val

    return jsonify({
        "code": 200,
        "message": "success",
        "data": records
    }), 200

@analysis_bp.get("/price")
def get_price_analysis():
    df = _get_analysis_df()
    result = analyze_price(df)
    if "distribution" in result:
        for item in result["distribution"]:
            r = item.get("range") or item.get("bin") or ""
            item["range"] = r
            item["bin"] = r
            item["count"] = int(item.get("count", 0))
    return jsonify({
        "code": 200,
        "message": "success",
        "data": result
    }), 200

@analysis_bp.get("/rating")
def get_rating_analysis():
    df = _get_analysis_df()
    result = analyze_rating(df)
    if "distribution" in result:
        for item in result["distribution"]:
            r = item.get("range") or item.get("bin") or ""
            item["range"] = r
            item["bin"] = r
            item["count"] = int(item.get("count", 0))
    return jsonify({
        "code": 200,
        "message": "success",
        "data": result
    }), 200

@analysis_bp.get("/ranking")
def get_ranking():
    df = _get_analysis_df()
    tops = get_top_products(df, top_n=10)
    return jsonify({
        "code": 200,
        "message": "success",
        "data": tops
    }), 200
