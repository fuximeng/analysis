# from flask import Blueprint, jsonify, request
# from crawler.spider import DummyJSONSpider
# from database.db import SessionLocal
# from database.models import CrawlTask
# from routes.auth_middleware import admin_required
#
# crawler_bp = Blueprint("crawler", __name__, url_prefix="/crawler")
#
# @crawler_bp.get("/tasks")
# @admin_required
# def list_crawl_tasks():
#     db = SessionLocal()
#     try:
#         tasks = db.query(CrawlTask).order_by(CrawlTask.id.desc()).all()
#         result = []
#         for t in tasks:
#             result.append({
#                 "id": t.id,
#                 "task_name": t.task_name,
#                 "status": t.status,
#                 "total_count": t.total_count,
#                 "success_count": t.success_count,
#                 "fail_count": t.fail_count,
#                 "started_at": t.started_at.strftime("%Y-%m-%d %H:%M:%S") if t.started_at else None,
#                 "finished_at": t.finished_at.strftime("%Y-%m-%d %H:%M:%S") if t.finished_at else None
#             })
#         return jsonify({
#             "code": 200,
#             "message": "success",
#             "data": result
#         }), 200
#     finally:
#         db.close()
#
# @crawler_bp.post("/run")
# @admin_required
# def trigger_crawl():
#     spider = DummyJSONSpider(limit=30)
#     try:
#         df = spider.run()
#         return jsonify({
#             "code": 200,
#             "message": "采集任务执行完成",
#             "data": {
#                 "count": len(df)
#             }
#         }), 200
#     except Exception as e:
#         return jsonify({
#             "code": 500,
#             "message": f"采集失败: {str(e)}",
#             "data": None
#         }), 500
from datetime import datetime

from flask import Blueprint, jsonify

from crawler.spider import DummyJSONSpider
from database.db import SessionLocal
from database.models import DataSource, CrawlTask, CrawlLog
from routes.auth_middleware import admin_required


crawler_bp = Blueprint("crawler", __name__, url_prefix="/crawler")


@crawler_bp.get("/tasks")
@admin_required
def list_crawl_tasks():
    """获取爬虫任务列表。"""
    db = SessionLocal()

    try:
        tasks = (
            db.query(CrawlTask)
            .order_by(CrawlTask.id.desc())
            .all()
        )

        result = []

        for task in tasks:
            result.append({
                "id": task.id,
                "task_name": task.task_name,
                "status": task.status,
                "total_count": task.total_count,
                "success_count": task.success_count,
                "fail_count": task.fail_count,
                "started_at": (
                    task.started_at.strftime("%Y-%m-%d %H:%M:%S")
                    if task.started_at
                    else None
                ),
                "finished_at": (
                    task.finished_at.strftime("%Y-%m-%d %H:%M:%S")
                    if task.finished_at
                    else None
                )
            })

        return jsonify({
            "code": 200,
            "message": "success",
            "data": result
        }), 200

    finally:
        db.close()


@crawler_bp.post("/run")
@admin_required
def trigger_crawl():
    """管理员触发 DummyJSON 爬虫任务。"""

    db = SessionLocal()
    task = None

    try:
        # ============================================================
        # 1. 获取 DummyJSON 数据源
        # ============================================================
        source = (
            db.query(DataSource)
            .filter(DataSource.name == "DummyJSON")
            .first()
        )

        if source is None:
            return jsonify({
                "code": 404,
                "message": "未找到 DummyJSON 数据源",
                "data": None
            }), 404

        # ============================================================
        # 2. 创建爬虫任务记录
        # ============================================================
        task = CrawlTask(
            source_id=source.id,
            task_name="DummyJSON 商品数据采集",
            status="running",
            total_count=0,
            success_count=0,
            fail_count=0,
            started_at=datetime.now()
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        # ============================================================
        # 3. 记录任务开始日志
        # ============================================================
        start_log = CrawlLog(
            task_id=task.id,
            level="info",
            message="开始执行 DummyJSON 商品数据采集任务"
        )

        db.add(start_log)
        db.commit()

        # ============================================================
        # 4. 执行现有爬虫
        # ============================================================
        spider = DummyJSONSpider(limit=30)
        df = spider.run()

        count = len(df)

        # ============================================================
        # 5. 更新任务为成功
        # ============================================================
        task.status = "success"
        task.total_count = count
        task.success_count = count
        task.fail_count = 0
        task.finished_at = datetime.now()

        db.add(task)

        # ============================================================
        # 6. 记录任务成功日志
        # ============================================================
        success_log = CrawlLog(
            task_id=task.id,
            level="info",
            message=f"DummyJSON 商品数据采集完成，共获取 {count} 条数据"
        )

        db.add(success_log)

        db.commit()

        # ============================================================
        # 7. 返回执行结果
        # ============================================================
        return jsonify({
            "code": 200,
            "message": "采集任务执行完成",
            "data": {
                "task_id": task.id,
                "status": task.status,
                "count": count,
                "success_count": task.success_count,
                "fail_count": task.fail_count
            }
        }), 200

    except Exception as e:
        # ============================================================
        # 8. 采集失败处理
        # ============================================================
        db.rollback()

        if task is not None:
            task.status = "failed"
            task.finished_at = datetime.now()

            error_log = CrawlLog(
                task_id=task.id,
                level="error",
                message=f"DummyJSON 商品数据采集失败：{str(e)}"
            )

            db.add(task)
            db.add(error_log)

            db.commit()

        return jsonify({
            "code": 500,
            "message": f"采集失败: {str(e)}",
            "data": {
                "task_id": task.id if task else None
            }
        }), 500
