from config import engine, test_connection
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库 Session 的上下文/依赖生成器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

__all__ = ["engine", "test_connection", "Base", "SessionLocal", "get_db"]
