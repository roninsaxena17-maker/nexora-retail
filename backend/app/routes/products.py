

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.database.connection import SessionLocal
from app.database.models import Product, Category
from app.kafka.producer import publish_event

router = APIRouter(prefix="/products", tags=["Products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: float = Field(gt=0)
    image_url: str | None = None
    stock_quantity: int = Field(default=0, ge=0)
    category_id: int | None = None
    city_id: int | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    image_url: str | None = None
    stock_quantity: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    city_id: int | None = None


def product_data(product):
    return {
        "product_id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "image_url": product.image_url,
        "stock_quantity": product.stock_quantity,
        "category": product.category.name if product.category else None,
        "city": product.city.name if product.city else None
    }


def load_product(db, product_id):
    return (
        db.query(Product)
        .options(
            joinedload(Product.category),
            joinedload(Product.city)
        )
        .filter(Product.id == product_id)
        .first()
    )


# GET ALL PRODUCTS WITH OPTIONAL CATEGORY FILTERING
@router.get("/")
def get_products(
    category_id: int | None = Query(default=None, gt=0),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Product)
        .options(
            joinedload(Product.category),
            joinedload(Product.city)
        )
    )

    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    if category:
        query = query.join(Category).filter(
            Category.name.ilike(category.strip())
        )

    products = query.all()

    return [
        product_data(product)
        for product in products
    ]


# GET SINGLE PRODUCT
@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = load_product(db, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product_data(product)


# CREATE PRODUCT
@router.post("/", status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db)
):
    if payload.category_id is not None:
        category_exists = db.query(Category).filter(
            Category.id == payload.category_id
        ).first()

        if not category_exists:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

    product = Product(**payload.model_dump())

    try:
        db.add(product)
        db.commit()
        db.refresh(product)

        product = load_product(db, product.id)

        event_published = False

        try:
            publish_event(
                "product_created",
                product_data(product)
            )
            event_published = True
        except Exception as error:
            print(f"Kafka publish failed: {error}")

        return {
            "message": "Product created successfully",
            "event_published": event_published,
            "product": product_data(product)
        }

    except Exception:
        db.rollback()
        raise


# UPDATE PRODUCT
@router.put("/{product_id}")
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    changes = payload.model_dump(exclude_unset=True)

    if changes.get("category_id") is not None:
        category_exists = db.query(Category).filter(
            Category.id == changes["category_id"]
        ).first()

        if not category_exists:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

    for field, value in changes.items():
        setattr(product, field, value)

    try:
        db.commit()

        product = load_product(db, product_id)

        event_published = False

        try:
            publish_event(
                "product_updated",
                product_data(product)
            )
            event_published = True
        except Exception as error:
            print(f"Kafka publish failed: {error}")

        return {
            "message": "Product updated successfully",
            "event_published": event_published,
            "product": product_data(product)
        }

    except Exception:
        db.rollback()
        raise

