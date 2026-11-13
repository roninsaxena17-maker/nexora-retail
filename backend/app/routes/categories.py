
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Category, Product

router = APIRouter(prefix="/categories", tags=["Categories"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.name).all()

    return [
        {
            "id": category.id,
            "name": category.name,
            "product_count": db.query(Product).filter(
                Product.category_id == category.id
            ).count()
        }
        for category in categories
    ]


@router.post("/", status_code=201)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db)
):
    name = payload.name.strip()

    if len(name) < 2:
        raise HTTPException(
            status_code=422,
            detail="Category name must contain at least 2 characters"
        )

    existing = db.query(Category).filter(
        Category.name.ilike(name)
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )

    category = Category(name=name)

    try:
        db.add(category)
        db.commit()
        db.refresh(category)

        return {
            "message": "Category created successfully",
            "id": category.id,
            "name": category.name
        }

    except Exception:
        db.rollback()
        raise

