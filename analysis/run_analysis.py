import pandas as pd
from pathlib import Path
from analysis.load_data import load_products
from analysis.basic_analysis import calculate_basic_statistics
from analysis.category_analysis import analyze_categories
from analysis.price_analysis import analyze_price
from analysis.rating_analysis import analyze_rating
from analysis.product_analysis import get_top_products

BASE_DIR = Path(__file__).resolve().parent.parent

def get_analysis_dataframe():
    """优先从 MySQL 加载数据，如果数据库暂未启动则自动读取本地清洗好的 CSV"""
    try:
        df = load_products()
        if not df.empty:
            print("【数据来源】成功从 MySQL (products表) 读取数据")
            return df
    except Exception as e:
        print(f"【提示】连接 MySQL 失败 ({e})，正在回退读取本地 CSV 文件...")

    # 回退到本地 CSV 文件
    csv_paths = [
        BASE_DIR / "data" / "cleaned" / "products_cleaned.csv",
        BASE_DIR / "data" / "raw" / "products_raw.csv",
        BASE_DIR / "data" / "raw" / "dummyjson_products.csv"
    ]
    for path in csv_paths:
        if path.exists():
            print(f"【数据来源】读取本地数据文件: {path.name}")
            return pd.read_csv(path)

    print("【错误】未找到任何可用数据！")
    return pd.DataFrame()

def run_all_analysis():
    df = get_analysis_dataframe()
    if df.empty:
        return

    print(f"共加载有效商品数据: {len(df)} 条\n")

    # 1. 基础核心 KPI 指标
    print("=" * 30 + " 1. 核心 KPI 基础指标 " + "=" * 30)
    basic_stats = calculate_basic_statistics(df)
    for k, v in basic_stats.items():
        if isinstance(v, float):
            print(f"  {k:20s}: {v:.2f}")
        else:
            print(f"  {k:20s}: {v}")

    # 2. 价格统计与价格区间分布
    print("\n" + "=" * 30 + " 2. 价格分析与区间分布 " + "=" * 30)
    price_stats = analyze_price(df)
    print(f"  平均价格: {price_stats['average_price']:.2f} 元")
    print(f"  中位数价格: {price_stats['median_price']:.2f} 元")
    print(f"  最高/最低价格: {price_stats['max_price']:.2f} / {price_stats['min_price']:.2f} 元")
    print("  价格区间分布情况:")
    for dist in price_stats["distribution"]:
        bar = '#' * (dist['count'] // 2)
        print(f"    [{dist['range']:<10s}]: {dist['count']:3d} 件 {bar}")

    # 3. 评分统计与评分区间分布
    print("\n" + "=" * 30 + " 3. 评分分析与区间分布 " + "=" * 30)
    rating_stats = analyze_rating(df)
    print(f"  平均评分: {rating_stats['average_rating']:.2f} 分")
    print(f"  中位数评分: {rating_stats['median_rating']:.2f} 分")
    print(f"  最高/最低评分: {rating_stats['max_rating']:.2f} / {rating_stats['min_rating']:.2f} 分")
    print("  评分区间分布情况:")
    for dist in rating_stats["distribution"]:
        bar = '#' * (dist['count'] // 2)
        print(f"    [{dist['range']:<10s}]: {dist['count']:3d} 件 {bar}")

    # 4. 商品排行榜 Top 5
    print("\n" + "=" * 30 + " 4. 商品排行榜 (Top 5) " + "=" * 30)
    tops = get_top_products(df, top_n=5)
    title_key = "title" if "title" in df.columns else "product_name"

    print("\n  >>【评分最高 Top 5】")
    for i, item in enumerate(tops["top_rated"], 1):
        print(f"    {i}. {str(item.get(title_key, ''))[:30]:<30s} | 评分: {item.get('rating')} | 价格: {item.get('price')} 元")

    print("\n  >>【价格最高 Top 5】")
    for i, item in enumerate(tops["top_expensive"], 1):
        print(f"    {i}. {str(item.get(title_key, ''))[:30]:<30s} | 价格: {item.get('price')} 元 | 评分: {item.get('rating')}")

    print("\n  >>【性价比/低价 Top 5】")
    for i, item in enumerate(tops["top_cheapest"], 1):
        print(f"    {i}. {str(item.get(title_key, ''))[:30]:<30s} | 价格: {item.get('price')} 元 | 评分: {item.get('rating')}")

    print("\n  >>【库存最高 Top 5】")
    for i, item in enumerate(tops["top_stock"], 1):
        print(f"    {i}. {str(item.get(title_key, ''))[:30]:<30s} | 库存: {item.get('stock')} 件")

    # 5. 分类统计汇总
    print("\n" + "=" * 30 + " 5. 商品分类统计汇总 (前 5 个品类) " + "=" * 30)
    category_res = analyze_categories(df)
    print(category_res.head(5).to_string())
    print("\n" + "=" * 80)

if __name__ == "__main__":
    run_all_analysis()
