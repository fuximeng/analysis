[README.md](https://github.com/user-attachments/files/34508562/README.md)
# 电商数据分析系统

> 基于 Flask + MySQL + ECharts 的全栈电商商品数据采集与可视化分析平台

---

## 项目简介

本系统是一个面向电商领域的数据分析 Web 应用，支持商品数据的**自动化采集**、**数据质量检查与清洗**、**多维度统计分析**以及**交互式可视化大屏展示**。系统采用前后端不分离的 Flask MVC 架构，实现了基于角色的访问控制（RBAC），区分管理员与普通用户的操作权限边界。

---

## 技术栈

| 层次 | 技术 / 组件 |
| :--- | :--- |
| **后端框架** | Python 3.x · Flask 3.1 · Flask-SQLAlchemy |
| **数据库** | MySQL 8.x（PyMySQL 驱动 · SQLAlchemy 2.0 ORM） |
| **数据采集** | Requests · DummyJSON API · 分页流控 · 自动重试 |
| **数据处理** | Pandas · NumPy · 自定义清洗与质检管道 |
| **前端模板** | Jinja2 · HTML5 · ECharts（柱状图 / 饼图 / 折线图） |
| **认证与权限** | Flask Session · 密码哈希（Argon2） · RBAC 角色拦截中间件 |
| **文件处理** | CSV 导入 · openpyxl · 最大支持 100 MB 上传 |
| **测试框架** | pytest · 单元测试 · 接口集成测试 |
| **环境配置** | python-dotenv（`.env` 文件） |
| **其他依赖** | Scrapy · Selenium · jieba · Matplotlib |

---

## 功能模块

```
├── 用户管理      注册 / 登录 / 退出 / 个人信息查看
├── 数据采集      商品数据采集 / 分页批量拉取 / 异常自动重试 / 任务日志
├── 数据管理      商品查询（关键字 + 分类筛选 + 分页）/ CSV 外部数据集导入
├── 数据质检      字段完整性 / 类型兼容性 / 缺失值 / 极端价格异常检测
├── 数据清洗      去重 / 缺失值填补 / 脏数据剔除 / 标准化批量写库
├── 数据分析      基础大盘统计 / 分类维度聚合 / 价格 / 评分多维度分析
├── 可视化大屏    ECharts 交互式图表（柱状图 / 饼图 / 折线图）
└── 系统支撑      RBAC 权限控制 / 操作审计日志 / 全局异常处理
```

---

## 目录结构

```
ecommerce-analysis2/
├── app.py                  # Flask 应用工厂与入口
├── config.py               # 全局配置（读取 .env）
├── .env.example            # 环境变量模板
├── requirements.txt        # Python 依赖清单
├── ecommerce_analysis.sql  # 数据库建表脚本
│
├── routes/                 # 路由蓝图层（Controller）
│   ├── auth.py             # 注册 / 登录 / 退出
│   ├── auth_middleware.py  # 鉴权与 RBAC 拦截器
│   ├── products.py         # 商品数据查询接口
│   ├── crawler.py          # 采集任务管理接口
│   ├── analysis.py         # 统计分析接口
│   ├── dataset.py          # 数据集管理接口
│   ├── upload.py           # CSV 文件上传接口
│   ├── admin.py            # 管理员专属视图
│   ├── user.py             # 普通用户视图
│   └── categories.py       # 商品分类接口
│
├── crawler/                # 数据采集引擎
│   ├── spider.py           # 核心爬虫调度器
│   ├── request.py          # HTTP 请求封装（含重试策略）
│   ├── dummyjson.py        # DummyJSON 数据源适配器
│   ├── parser.py           # 响应数据解析器
│   └── logger.py           # 采集日志记录器
│
├── analysis/               # 数据分析引擎
│   ├── data_quality.py     # 数据质量检查
│   ├── data_clean.py       # 数据清洗规则
│   ├── basic_analysis.py   # 基础大盘统计
│   ├── category_analysis.py# 分类维度分析
│   ├── price_analysis.py   # 价格分布分析
│   ├── rating_analysis.py  # 评分分析
│   └── analysis_runner.py  # 分析任务统一调度
│
├── database/               # 数据访问层
│   ├── models.py           # SQLAlchemy 数据模型（ORM 实体）
│   ├── db.py               # 数据库连接与会话管理
│   └── insert_products.py  # 批量数据写入工具
│
├── templates/              # Jinja2 HTML 模板
│   ├── login.html
│   ├── register.html
│   ├── user/               # 普通用户视图
│   └── admin/              # 管理员视图
│
├── static/                 # 静态资源（CSS / JS / ECharts）
├── data/                   # 原始采集数据与 CSV 存储
├── logs/                   # 运行日志目录
└── tests/                  # pytest 测试套件
```

---

## 快速开始

### 环境要求

| 组件 | 版本要求 |
| :--- | :--- |
| Python | 3.10 及以上 |
| MySQL | 8.0 及以上 |
| pip | 最新版 |

### 1. 克隆项目

```bash
git clone <仓库地址>
cd ecommerce-analysis2
```

### 2. 创建并激活虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

将 `.env.example` 复制为 `.env` 并按实际情况修改：

```bash
cp .env.example .env
```

```ini
# .env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here   # 请修改为随机强密钥

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password   # 修改为实际数据库密码
DB_NAME=ecommerce_analysis
```

### 5. 初始化数据库

在 MySQL 中执行建表脚本：

```bash
mysql -u root -p < ecommerce_analysis.sql
```

或使用 MySQL 客户端（Navicat / DBeaver / MySQL Workbench）导入 `ecommerce_analysis.sql`。

### 6. 验证数据库连接

```bash
python config.py
# 输出 "MySQL 数据库连接成功！" 即表示配置正确
```

### 7. 启动服务

```bash
python app.py
```

服务默认运行在：**http://127.0.0.1:5000**

---

## 默认账号

> [!IMPORTANT]
> 首次运行请通过注册页面创建账号，或通过数据库脚本插入默认管理员账号。

| 角色 | 说明 |
| :--- | :--- |
| **管理员（admin）** | 可执行数据采集、质检、清洗、查看日志等高权限操作 |
| **普通用户（user）** | 仅可访问商品查询、统计分析、可视化大屏等只读视图 |

---

## 核心接口一览（RESTful API）

| 方法 | 路径 | 功能 | 鉴权 |
| :--- | :--- | :--- | :---: |
| POST | `/api/users` | 用户注册 | 否 |
| POST | `/api/sessions` | 用户登录 | 否 |
| DELETE | `/api/sessions` | 退出登录 | 是 |
| GET | `/api/users/me` | 获取当前用户信息 | 是 |
| GET | `/api/products` | 商品分页查询（关键字+分类） | 否 |
| GET | `/api/products/{id}` | 获取商品详情 | 否 |
| POST | `/api/crawl-tasks` | 创建采集任务 | 管理员 |
| GET | `/api/crawl-tasks` | 查询采集任务列表 | 管理员 |
| POST | `/api/crawl-tasks/{id}/execution` | 执行采集任务 | 管理员 |
| POST | `/api/data-quality` | 执行数据质量检查 | 管理员 |
| POST | `/api/data-cleaning` | 执行数据清洗入库 | 管理员 |
| POST | `/api/products/import-csv` | 导入 CSV 数据集 | 管理员 |
| GET | `/api/analytics/products` | 商品基础大盘统计 | 否 |
| GET | `/api/analytics/categories` | 分类维度统计分析 | 否 |
| GET | `/api/logs` | 操作审计日志 | 管理员 |
| GET | `/health` | 服务健康检查 | 否 |

---

## 运行测试

```bash
# 运行全部测试
pytest

# 运行指定测试文件
pytest tests/test_api.py -v

# 生成测试覆盖率报告
pytest --cov=. --cov-report=html
```

---

## 健康检查

```bash
curl http://127.0.0.1:5000/health
# 返回：{"code": 200, "message": "ok", "data": {"service": "flask"}}
```

---

## 注意事项

> [!WARNING]
> 请勿将含有真实密码的 `.env` 文件提交至版本控制系统（已在 `.gitignore` 中排除）。

> [!NOTE]
> 本系统数据采集目前对接 **DummyJSON** 等公开模拟电商 API，不涉及对淘宝、京东等商业平台的爬取（需商业授权，属本期范围边界之外）。

> [!TIP]
> CSV 导入文件最大支持 **100 MB**。若导入失败，请检查文件字段结构是否与系统预设规范一致。

---

## 许可证

本项目仅供学术研究与毕业设计使用，请勿用于商业目的。
