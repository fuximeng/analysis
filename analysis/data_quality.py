from crawler.logger import logger

def check_data_quality(df):
    """
    检查商品数据质量
    """
    logger.info("开始进行数据质量检查")

    if df.empty:
        logger.warning("数据为空，无法进行质量检查")
        return

    # 1. 检查缺失值
    logger.info("缺失值检查：")
    missing = df.isnull().sum()
    for column, count in missing.items():
        if count > 0:
            logger.warning(f"字段 {column} 存在 {count} 条缺失值")

    # 2. 检查重复商品
    duplicate_count = df["product_id"].duplicated().sum() if "product_id" in df else 0
    if duplicate_count > 0:
        logger.warning(f"发现 {duplicate_count} 条重复商品")
    else:
        logger.info("未发现重复商品")

    # 3. 检查商品 ID
    if "product_id" in df and df["product_id"].isnull().sum() == 0:
        logger.info("商品 ID 检查通过")

    # 4. 检查商品名称
    title_col = "product_name" if "product_name" in df else "title"
    if title_col in df and df[title_col].isnull().sum() == 0:
        logger.info("商品名称检查通过")

    # 5. 检查价格
    if "price" in df:
        invalid_price = (df["price"] <= 0).sum()
        if invalid_price > 0:
            logger.warning(f"发现 {invalid_price} 条价格异常数据")
        else:
            logger.info("商品价格检查通过")

    # 6. 检查评分
    if "rating" in df:
        invalid_rating = ((df["rating"] < 0) | (df["rating"] > 5)).sum()
        if invalid_rating > 0:
            logger.warning(f"发现 {invalid_rating} 条评分异常数据")
        else:
            logger.info("商品评分检查通过")

    logger.info("数据质量检查完成")
