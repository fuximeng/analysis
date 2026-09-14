import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 加载 .env 环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-me')

    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_NAME = os.getenv('DB_NAME', 'ecommerce_analysis')

    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}'
        f'@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    )
    DATABASE_URL = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# 提供全局 SQLAlchemy engine
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_pre_ping=True
)


def test_connection():
    """测试 MySQL 数据库连接"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            print('MySQL 数据库连接成功！')
            print(f'测试结果：{result.scalar()}')
            return True
    except Exception as e:
        print('MySQL 数据库连接失败！')
        print(f'错误信息：{e}')
        return False


if __name__ == '__main__':
    test_connection()
