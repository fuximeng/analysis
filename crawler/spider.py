from pathlib import Path
import pandas as pd
from crawler.logger import logger
from crawler.request import fetch_products
from crawler.parser import parse_products

BASE_DIR = Path(__file__).resolve().parent.parent

class DummyJSONSpider:
    """DummyJSON 电商商品数据爬虫"""

    def __init__(self, limit: int = 30):
        self.limit = limit
        self.raw_data_dir = BASE_DIR / "data" / "raw"
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

    def crawl_all(self):
        """分页采集所有商品数据"""
        all_products = []
        skip = 0

        while True:
            logger.info(f"正在获取数据：skip={skip}")
            data = fetch_products(limit=self.limit, skip=skip)
            if not data:
                break

            products = data.get("products", [])
            if not products:
                break

            all_products.extend(products)
            total = data.get("total", 0)
            skip += self.limit

            logger.info(f"当前获取：{len(all_products)} / {total}")
            if skip >= total:
                break

        return {"products": all_products}

    def save_raw_data(self, df: pd.DataFrame):
        """保存原始数据到 CSV 文件"""
        if df.empty:
            logger.warning("没有数据可以保存")
            return

        file_path = self.raw_data_dir / "products_raw.csv"
        legacy_file_path = self.raw_data_dir / "dummyjson_products.csv"

        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        df.to_csv(legacy_file_path, index=False, encoding="utf-8-sig")

        logger.info(f"原始数据保存成功：{file_path}，数据量：{len(df)}")
        return file_path

    def run(self):
        """执行完整采集流程"""
        logger.info("开始采集 DummyJSON 商品数据...")
        data = self.crawl_all()
        df = parse_products(data)
        saved_path = self.save_raw_data(df)
        logger.info("采集完成！")
        return df

def crawl_all_products(limit=30):
    spider = DummyJSONSpider(limit=limit)
    return spider.crawl_all()

def save_data(df):
    spider = DummyJSONSpider()
    return spider.save_raw_data(df)

if __name__ == "__main__":
    spider = DummyJSONSpider()
    df = spider.run()
    print(df.head())
