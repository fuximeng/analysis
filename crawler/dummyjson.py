from crawler.spider import DummyJSONSpider, crawl_all_products, save_data
from crawler.request import fetch_products, BASE_URL
import crawler.request as requests_module
from crawler.parser import parse_products
from crawler.logger import logger
from analysis.data_quality import check_data_quality
from analysis.data_clean import clean_data
import requests

def main():
    logger.info("开始采集 DummyJSON 商品数据...")
    data = crawl_all_products()
    df = parse_products(data)
    check_data_quality(df)
    df = clean_data(df)
    save_data(df)
    logger.info("采集完成！")

if __name__ == "__main__":
    main()
