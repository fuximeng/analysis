from datetime import datetime
import pandas as pd

def parse_products(data):
    """
    将 API 返回的数据转换成 DataFrame
    """
    if not data:
        return pd.DataFrame()

    products = data.get("products", [])
    result = []
    crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for product in products:
        result.append({
            "product_id": product.get("id"),
            "product_name": product.get("title"),
            "category": product.get("category"),
            "brand": product.get("brand"),
            "price": product.get("price"),
            "discount": product.get("discountPercentage"),
            "rating": product.get("rating"),
            "stock": product.get("stock"),
            "description": product.get("description"),
            "thumbnail": product.get("thumbnail"),
            "source": "dummyjson",
            "crawl_time": crawl_time
        })

    return pd.DataFrame(result)
