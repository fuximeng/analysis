import pandas as pd

from database.db import engine


def load_products():
    """从 MySQL products 表读取商品数据"""

    sql = "SELECT * FROM products"

    df = pd.read_sql(sql, con=engine)

    return df


if __name__ == "__main__":
    print("开始从 MySQL 读取商品数据...")

    df = load_products()

    print(f"数据读取完成：{len(df)} 条")
    print(f"字段数量：{len(df.columns)}")
    print(f"字段列表：{list(df.columns)}")

    print("\n前 5 条数据：")
    print(df.head())