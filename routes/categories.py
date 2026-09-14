from flask import Blueprint, jsonify
from database.db import SessionLocal
from database.models import Category, Product

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")

@categories_bp.get("")
def list_categories():
    db = SessionLocal()
    try:
        cats = db.query(Category).all()
        result = []
        for c in cats:
            product_count = db.query(Product).filter_by(category_id=c.id).count()
            result.append({
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "product_count": product_count,
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None
            })
        return jsonify({
            "code": 200,
            "message": "success",
            "data": result
        }), 200
    finally:
        db.close()
