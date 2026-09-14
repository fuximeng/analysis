import math
from flask import Blueprint, request, jsonify
from database.db import SessionLocal
from database.models import Product, Category
from routes.auth_middleware import admin_required

products_bp = Blueprint("products", __name__, url_prefix="/products")

@products_bp.get("")
def list_products():
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1

    try:
        page_size = max(1, min(100, int(request.args.get("page_size", 10))))
    except (ValueError, TypeError):
        page_size = 10

    keyword = request.args.get("keyword", "").strip()
    category_name = request.args.get("category", "").strip()
    
    raw_sort_by = request.args.get("sort_by", "id")
    allowed_sorts = {"id", "title", "price", "rating", "stock", "discount_percentage", "created_at"}
    sort_by = raw_sort_by if raw_sort_by in allowed_sorts else "id"
    order = request.args.get("order", "asc")

    db = SessionLocal()
    try:
        query = db.query(Product)
        if keyword:
            query = query.filter(Product.title.ilike(f"%{keyword}%"))
        if category_name:
            cat = db.query(Category).filter_by(name=category_name).first()
            if cat:
                query = query.filter(Product.category_id == cat.id)
            else:
                return jsonify({
                    "code": 200,
                    "message": "success",
                    "data": {
                        "total": 0,
                        "page": page,
                        "page_size": page_size,
                        "pages": 0,
                        "items": []
                    }
                }), 200

        sort_column = getattr(Product, sort_by, Product.id)
        if order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        total = query.count()
        pages = math.ceil(total / page_size) if total > 0 else 0
        products = query.offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for p in products:
            items.append({
                "id": p.id,
                "source_product_id": p.source_product_id,
                "title": p.title,
                "category_id": p.category_id,
                "category_name": p.category.name if p.category else None,
                "price": float(p.price) if p.price is not None else 0.0,
                "discount_percentage": float(p.discount_percentage) if p.discount_percentage is not None else 0.0,
                "rating": float(p.rating) if p.rating is not None else None,
                "stock": p.stock,
                "brand": p.brand,
                "description": p.description,
                "thumbnail": p.thumbnail,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None
            })

        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": pages,
                "items": items
            }
        }), 200
    finally:
        db.close()

@products_bp.get("/<int:product_id>")
def get_product_detail(product_id):
    db = SessionLocal()
    try:
        p = db.query(Product).filter_by(id=product_id).first()
        if not p:
            return jsonify({"code": 404, "message": "商品不存在", "data": None}), 404

        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "id": p.id,
                "source_product_id": p.source_product_id,
                "title": p.title,
                "category_id": p.category_id,
                "category_name": p.category.name if p.category else None,
                "price": float(p.price) if p.price is not None else 0.0,
                "discount_percentage": float(p.discount_percentage) if p.discount_percentage is not None else 0.0,
                "rating": float(p.rating) if p.rating is not None else None,
                "stock": p.stock,
                "brand": p.brand,
                "description": p.description,
                "thumbnail": p.thumbnail,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
                "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M:%S") if p.updated_at else None
            }
        }), 200
    finally:
        db.close()
