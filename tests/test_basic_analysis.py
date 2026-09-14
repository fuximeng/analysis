import pandas as pd

from analysis.basic_analysis import calculate_basic_statistics


def test_calculate_basic_statistics():
    df = pd.DataFrame({
        "price": [10, 20, 30],
        "rating": [3, 4, 5],
        "discount": [10, 20, 30],
        "stock": [10, 20, 30],
        "category": ["A", "A", "B"],
        "brand": ["X", "Y", "X"]
    })

    result = calculate_basic_statistics(df)

    assert result["product_count"] == 3
    assert result["average_price"] == 20
    assert result["max_price"] == 30
    assert result["min_price"] == 10
    assert result["average_rating"] == 4
    assert result["average_discount"] == 20
    assert result["total_stock"] == 60
    assert result["category_count"] == 2
    assert result["brand_count"] == 2