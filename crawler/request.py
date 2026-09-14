import time
import requests
from crawler.logger import logger

BASE_URL = "https://dummyjson.com/products"

def fetch_products(limit=30, skip=0, retries=3, timeout=10):
    """
    从 DummyJSON 获取商品数据

    :param limit: 每次获取商品数量
    :param skip: 跳过的商品数量
    :param retries: 请求失败后的重试次数
    :param timeout: HTTP 请求超时时间
    """
    params = {
        "limit": limit,
        "skip": skip
    }

    for attempt in range(retries + 1):
        try:
            logger.info(f"请求商品数据：skip={skip}, limit={limit}")
            response = requests.get(
                BASE_URL,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            if attempt < retries:
                logger.warning(f"请求失败，第 {attempt + 1} 次尝试：{e}")
                wait_time = attempt + 1
                logger.info(f"{wait_time} 秒后进行第 {attempt + 2} 次尝试")
                time.sleep(wait_time)
            else:
                logger.error(f"请求失败，已达到最大重试次数：{e}")
                return None
