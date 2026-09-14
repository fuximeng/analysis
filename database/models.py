from datetime import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Integer,
    SmallInteger,
    Numeric,
    Text,
    DateTime,
    ForeignKey,
    Index,
    func
)
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import relationship
from database.db import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_role", "role"),
        {"comment": "系统用户表", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    role = Column(String(20), nullable=False, default="user", server_default="user", comment="角色：user/admin")
    status = Column(TINYINT, nullable=False, default=1, server_default="1", comment="用户状态：1=正常 0=禁用")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now(), comment="更新时间")

    analysis_records = relationship("AnalysisRecord", back_populates="user", cascade="all, delete-orphan")
    datasets = relationship("UserDataset", back_populates="user", cascade="all, delete-orphan")
    operation_logs = relationship("OperationLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        {"comment": "分类表", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    name = Column(String(100), nullable=False, unique=True, comment="分类名称")
    description = Column(String(255), nullable=True, comment="分类描述")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now(), comment="更新时间")

    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("idx_category_id", "category_id"),
        Index("idx_source_id", "source_id"),
        Index("idx_source_product_id", "source_product_id"),
        Index("idx_brand", "brand"),
        {"comment": "商品表", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    source_product_id = Column(String(100), nullable=True, comment="数据源商品 ID")
    title = Column(String(255), nullable=False, comment="商品名称")
    category_id = Column(BIGINT(unsigned=True), ForeignKey("categories.id"), nullable=True, comment="分类 ID")
    price = Column(Numeric(10, 2), nullable=False, default=0.00, server_default="0.00", comment="商品价格")
    discount_percentage = Column(Numeric(5, 2), nullable=True, default=0.00, server_default="0.00", comment="折扣百分比")
    rating = Column(Numeric(3, 2), nullable=True, comment="评分")
    stock = Column(Integer, nullable=False, default=0, server_default="0", comment="库存")
    brand = Column(String(100), nullable=True, comment="品牌")
    description = Column(Text, nullable=True, comment="商品描述")
    thumbnail = Column(String(500), nullable=True, comment="商品图片")
    source_id = Column(BIGINT(unsigned=True), ForeignKey("data_sources.id"), nullable=True, comment="数据源 ID")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now(), comment="更新时间")

    category = relationship("Category", back_populates="products")
    source = relationship("DataSource", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title}', price={self.price})>"

class DataSource(Base):
    __tablename__ = "data_sources"
    __table_args__ = (
        Index("idx_source_type", "source_type"),
        Index("idx_status", "status"),
        {"comment": "数据源表", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    name = Column(String(100), nullable=False, unique=True, comment="数据源名称")
    source_type = Column(String(30), nullable=False, comment="数据源类型：API/CSV/Web")
    url = Column(String(500), nullable=True, comment="数据源地址")
    status = Column(TINYINT, nullable=False, default=1, server_default="1", comment="状态：1=启用 0=禁用")
    description = Column(Text, nullable=True, comment="描述")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), comment="创建时间")

    products = relationship("Product", back_populates="source")
    crawl_tasks = relationship("CrawlTask", back_populates="source")

    def __repr__(self):
        return f"<DataSource(id={self.id}, name='{self.name}', source_type='{self.source_type}')>"

class CrawlTask(Base):
    __tablename__ = "crawl_tasks"
    __table_args__ = (
        Index("idx_source_id", "source_id"),
        Index("idx_status", "status"),
        {"comment": "爬虫任务表", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    source_id = Column(BIGINT(unsigned=True), ForeignKey("data_sources.id"), nullable=False, comment="数据源 ID")
    task_name = Column(String(100), nullable=False, comment="任务名称")
    status = Column(String(30), nullable=False, default="pending", server_default="pending", comment="任务状态")
    total_count = Column(Integer, nullable=False, default=0, server_default="0", comment="总数据量")
    success_count = Column(Integer, nullable=False, default=0, server_default="0", comment="成功数量")
    fail_count = Column(Integer, nullable=False, default=0, server_default="0", comment="失败数量")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    finished_at = Column(DateTime, nullable=True, comment="完成时间")

    source = relationship("DataSource", back_populates="crawl_tasks")
    logs = relationship("CrawlLog", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CrawlTask(id={self.id}, task_name='{self.task_name}', status='{self.status}')>"

class CrawlLog(Base):
    __tablename__ = "crawl_logs"
    __table_args__ = (
        Index("idx_task_id", "task_id"),
        Index("idx_level", "level"),
        Index("idx_created_at", "created_at"),
        {"comment": "爬虫日志表", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    task_id = Column(BIGINT(unsigned=True), ForeignKey("crawl_tasks.id"), nullable=False, comment="任务 ID")
    level = Column(String(20), nullable=False, default="info", server_default="info", comment="日志级别")
    message = Column(Text, nullable=False, comment="日志内容")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), comment="时间")

    task = relationship("CrawlTask", back_populates="logs")

    def __repr__(self):
        return f"<CrawlLog(id={self.id}, task_id={self.task_id}, level='{self.level}')>"

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_dataset_id", "dataset_id"),
        Index("idx_analysis_type", "analysis_type"),
        {"comment": "分析记录表", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id"), nullable=False, comment="用户 ID")
    dataset_id = Column(BIGINT(unsigned=True), ForeignKey("user_datasets.id"), nullable=True, comment="数据集 ID")
    analysis_type = Column(String(50), nullable=False, comment="分析类型")
    result_summary = Column(Text, nullable=True, comment="分析摘要")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), comment="创建时间")

    user = relationship("User", back_populates="analysis_records")
    dataset = relationship("UserDataset", back_populates="analysis_records")

    def __repr__(self):
        return f"<AnalysisRecord(id={self.id}, user_id={self.user_id}, type='{self.analysis_type}')>"

class UserDataset(Base):
    __tablename__ = "user_datasets"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
        {"comment": "用户数据集表", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id"), nullable=False, comment="用户 ID")
    dataset_name = Column(String(100), nullable=False, comment="数据集名称")
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(String(500), nullable=False, comment="文件路径")
    row_count = Column(Integer, nullable=False, default=0, server_default="0", comment="数据行数")
    status = Column(String(30), nullable=False, default="uploaded", server_default="uploaded", comment="状态")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), comment="上传时间")

    user = relationship("User", back_populates="datasets")
    analysis_records = relationship("AnalysisRecord", back_populates="dataset")

    def __repr__(self):
        return f"<UserDataset(id={self.id}, name='{self.dataset_name}', rows={self.row_count})>"

class OperationLog(Base):
    __tablename__ = "operation_logs"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_operation", "operation"),
        Index("idx_created_at", "created_at"),
        {"comment": "操作日志表", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment="主键")
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id"), nullable=True, comment="操作用户 ID")
    operation = Column(String(100), nullable=False, comment="操作类型")
    target = Column(String(100), nullable=True, comment="操作对象")
    detail = Column(Text, nullable=True, comment="操作详情")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now(), comment="时间")

    user = relationship("User", back_populates="operation_logs")

    def __repr__(self):
        return f"<OperationLog(id={self.id}, operation='{self.operation}', target='{self.target}')>"
