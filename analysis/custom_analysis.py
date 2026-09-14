from pathlib import Path
import pandas as pd
import numpy as np

def analyze_custom_dataset(df: pd.DataFrame) -> dict:
    """
    对用户上传的自定义 CSV 数据集进行深度自动化统计与特征分析
    """
    if df.empty:
        return {
            "row_count": 0,
            "column_count": 0,
            "columns": [],
            "missing_stats": {},
            "numeric_stats": {},
            "category_stats": {}
        }

    row_count = int(len(df))
    column_count = int(len(df.columns))
    columns = list(df.columns)

    # 1. 缺失值统计
    missing_counts = df.isnull().sum()
    missing_stats = [
        {
            "column": col,
            "missing_count": int(count),
            "missing_rate": round(float(count / row_count * 100), 2)
        }
        for col, count in missing_counts.items()
    ]

    # 2. 数值型列统计（均值、中位数、最大值、最小值、标准差、直方图分布）
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_stats = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        c_min = round(float(series.min()), 2)
        c_max = round(float(series.max()), 2)
        c_mean = round(float(series.mean()), 2)
        c_median = round(float(series.median()), 2)
        c_std = round(float(series.std()), 2) if len(series) > 1 else 0.0

        # 直方图分箱 (最多5-8个区间)
        hist_bins = []
        try:
            counts, bin_edges = np.histogram(series, bins=min(6, max(2, int(series.nunique()))))
            for i in range(len(counts)):
                hist_bins.append({
                    "range": f"{round(float(bin_edges[i]), 1)}~{round(float(bin_edges[i+1]), 1)}",
                    "count": int(counts[i])
                })
        except Exception:
            pass

        numeric_stats[col] = {
            "min": c_min,
            "max": c_max,
            "mean": c_mean,
            "median": c_median,
            "std": c_std,
            "histogram": hist_bins
        }

    # 3. 分类型列统计（前 10 大类别及其频数）
    category_cols = [c for c in df.columns if c not in numeric_cols]
    category_stats = {}
    for col in category_cols:
        val_counts = df[col].fillna("Unknown").astype(str).value_counts().head(10)
        category_stats[col] = [
            {"name": str(cat), "value": int(cnt)}
            for cat, cnt in val_counts.items()
        ]

    return {
        "row_count": row_count,
        "column_count": column_count,
        "columns": columns,
        "missing_stats": missing_stats,
        "numeric_stats": numeric_stats,
        "category_stats": category_stats
    }
