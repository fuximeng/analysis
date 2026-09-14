
import pandas as pd

from analysis.load_data import load_products


def calculate_basic_statistics(df):
    """计算商品数据基础统计指标"""

    result = {
        "product_count": len(df),
        "average_price": df["price"].mean(),
        "max_price": df["price"].max(),
        "min_price": df["price"].min(),
        "average_rating": df["rating"].mean(),
        "average_discount": df["discount"].mean(),
        "total_stock": df["stock"].sum(),
        "category_count": df["category"].nunique(),
        "brand_count": df["brand"].nunique()
    }

    return result


if __name__ == "__main__":
    print("开始读取 MySQL 商品数据...")

    df = load_products()

    print(f"商品数据读取完成：{len(df)} 条")

    statistics = calculate_basic_statistics(df)

    print("\n========== 基础统计分析 ==========")
    print(f"商品总数：{statistics['product_count']}")
    print(f"平均价格：{statistics['average_price']:.2f}")
    print(f"最高价格：{statistics['max_price']:.2f}")
    print(f"最低价格：{statistics['min_price']:.2f}")
    print(f"平均评分：{statistics['average_rating']:.2f}")
    print(f"平均折扣：{statistics['average_discount']:.2f}")
    print(f"总库存：{statistics['total_stock']}")
    print(f"商品分类数：{statistics['category_count']}")
    print(f"品牌数量：{statistics['brand_count']}")

