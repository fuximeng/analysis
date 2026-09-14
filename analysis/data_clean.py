from pathlib import Path
import pandas as pd
from crawler.logger import logger

BASE_DIR = Path(__file__).resolve().parent.parent

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗商品数据
    """
    if df.empty:
        logger.warning("数据为空，无法进行清洗")
        return df

    logger.info("开始进行数据清洗")
    df = df.copy()
    original_count = len(df)

    # 1. 处理 brand 缺失值
    if "brand" in df:
        brand_missing = df["brand"].isnull().sum()
        if brand_missing > 0:
            df["brand"] = df["brand"].fillna("Unknown")
            logger.info(f"brand 缺失值已处理：{brand_missing} 条")

    # 2. 删除重复商品
    id_col = "product_id" if "product_id" in df else ("id" if "id" in df else None)
    if id_col:
        duplicate_count = df[id_col].duplicated().sum()
        if duplicate_count > 0:
            df = df.drop_duplicates(subset=[id_col], keep="first")
            logger.info(f"删除重复商品：{duplicate_count} 条")

    # 3. 删除价格异常数据
    if "price" in df:
        invalid_price = (df["price"] <= 0).sum()
        if invalid_price > 0:
            df = df[df["price"] > 0]
            logger.info(f"删除价格异常数据：{invalid_price} 条")

    # 4. 删除评分异常数据
    if "rating" in df:
        invalid_rating = ((df["rating"] < 0) | (df["rating"] > 5)).sum()
        if invalid_rating > 0:
            df = df[(df["rating"] >= 0) & (df["rating"] <= 5)]
            logger.info(f"删除评分异常数据：{invalid_rating} 条")

    cleaned_count = len(df)
    logger.info(f"数据清洗完成：{original_count} → {cleaned_count}")

    # 保存清洗后的数据到 data/cleaned/products_cleaned.csv
    cleaned_dir = BASE_DIR / "data" / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = cleaned_dir / "products_cleaned.csv"
    df.to_csv(cleaned_path, index=False, encoding="utf-8-sig")

    return df
