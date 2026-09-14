import pandas as pd
from sqlalchemy import text

from database.db import engine
from pathlib import Path  # 引入 pathlib 处理路径
# 1. Path(__file__).resolve() 获取当前脚本的绝对路径
# 2. .parent 获取 database 目录
# 3. 再加一个 .parent 退回到项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 4. 拼接出正确的绝对路径（优先读取 products_raw.csv，回退到 dummyjson_products.csv）
CSV_PATH = BASE_DIR / "data" / "raw" / "products_raw.csv"
if not CSV_PATH.exists():
    CSV_PATH = BASE_DIR / "data" / "raw" / "dummyjson_products.csv"


def insert_products():
    """将 CSV 商品数据导入 MySQL"""

    print("开始读取 CSV 数据...")

    df = pd.read_csv(CSV_PATH)

    print(f"CSV 数据读取完成：{len(df)} 条")

    # 确保 crawl_time 是 datetime 类型
    df["crawl_time"] = pd.to_datetime(df["crawl_time"])

    # 检查 product_id 是否重复
    duplicate_count = df["product_id"].duplicated().sum()

    if duplicate_count > 0:
        print(f"发现重复商品：{duplicate_count} 条")
        df = df.drop_duplicates(subset=["product_id"])

    print(f"准备写入 MySQL：{len(df)} 条")

    # 写入数据库
    df.to_sql(
        name="products",
        con=engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(f"数据写入完成：{len(df)} 条")


def check_count():
    """检查数据库中的商品数量"""

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT COUNT(*) FROM products")
        )

        count = result.scalar()

        print(f"MySQL 当前商品数量：{count}")


if __name__ == "__main__":
    insert_products()
    check_count()