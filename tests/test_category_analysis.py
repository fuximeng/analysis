
import pandas as pd

from analysis.category_analysis import analyze_categories


def test_analyze_categories():
    df = pd.DataFrame({
        "product_id": [1, 2, 3, 4],
        "category": ["beauty", "beauty", "fragrances", "furniture"],
        "price": [10, 20, 30, 40],
        "rating": [3, 4, 5, 4],
        "stock": [10, 20, 30, 40]
    })

    result = analyze_categories(df)

    # 商品数量
    assert result.loc["beauty", "count"] == 2
    assert result.loc["fragrances", "count"] == 1
    assert result.loc["furniture", "count"] == 1

    # 平均价格
    assert result.loc["beauty", "average_price"] == 15

    # 平均评分
    assert result.loc["beauty", "average_rating"] == 3.5

    # 总库存
    assert result.loc["beauty", "total_stock"] == 30

