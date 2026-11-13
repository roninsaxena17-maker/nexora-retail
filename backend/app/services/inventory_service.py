
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.database.models import Product


def deduct_stock(
    db: Session,
    product_id: int,
    quantity: int
):
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    result = db.execute(
        update(Product)
        .where(
            Product.id == product_id,
            Product.stock_quantity >= quantity
        )
        .values(
            stock_quantity=Product.stock_quantity - quantity
        )
    )

    if result.rowcount == 0:
        product_exists = (
            db.query(Product.id)
            .filter(Product.id == product_id)
            .first()
        )

        if not product_exists:
            raise ValueError("Product not found")

        raise ValueError("Insufficient stock")

    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )


def restore_stock(
    db: Session,
    product_id: int,
    quantity: int
):
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    result = db.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(
            stock_quantity=Product.stock_quantity + quantity
        )
    )

    if result.rowcount == 0:
        raise ValueError("Product not found")

    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

