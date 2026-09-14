
from analysis.load_data import load_products


def analyze_categories(df):
    """统计各商品分类的综合数据"""

    category_analysis = (
        df.groupby("category")
        .agg(
            count=("product_id", "count"),
            average_price=("price", "mean"),
            average_rating=("rating", "mean"),
            total_stock=("stock", "sum")
        )
        .sort_values("count", ascending=False)
    )

    return category_analysis


if __name__ == "__main__":
    print("开始读取 MySQL 商品数据...")

    df = load_products()

    print(f"数据读取完成：{len(df)} 条")

    category_analysis = analyze_categories(df)

    print("\n========== 商品分类综合分析 ==========")

    print(
        category_analysis.to_string(
            formatters={
                "average_price": "{:.2f}".format,
                "average_rating": "{:.2f}".format
            }
        )
    )

