
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Cart, CartItem, Customer, Product

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CartItemAdd(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class QuantityUpdate(BaseModel):
    quantity: int = Field(gt=0)


def get_or_create_cart(db, customer_id):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    cart = db.query(Cart).filter(
        Cart.customer_id == customer_id
    ).first()

    if not cart:
        cart = Cart(customer_id=customer_id)
        db.add(cart)
        db.flush()

    return cart


def get_cart_data(db, cart):
    items = db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).all()

    result = []
    total = 0

    for item in items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if not product:
            continue

        subtotal = product.price * item.quantity
        total += subtotal

        result.append({
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url,
            "quantity": item.quantity,
            "available_stock": product.stock_quantity,
            "subtotal": round(subtotal, 2)
        })

    return {
        "cart_id": cart.id,
        "customer_id": cart.customer_id,
        "items": result,
        "total_items": sum(
            item["quantity"] for item in result
        ),
        "total_price": round(total, 2)
    }


@router.get("/{customer_id}")
def get_cart(
    customer_id: int,
    db: Session = Depends(get_db)
):
    cart = get_or_create_cart(db, customer_id)
    db.commit()

    return get_cart_data(db, cart)


@router.post("/{customer_id}/items")
def add_to_cart(
    customer_id: int,
    payload: CartItemAdd,
    db: Session = Depends(get_db)
):
    try:
        cart = get_or_create_cart(db, customer_id)

        product = db.query(Product).filter(
            Product.id == payload.product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product.id
        ).first()

        new_quantity = payload.quantity

        if existing_item:
            new_quantity += existing_item.quantity

        if new_quantity > product.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock_quantity} units available"
            )

        if existing_item:
            existing_item.quantity = new_quantity
        else:
            db.add(
                CartItem(
                    cart_id=cart.id,
                    product_id=product.id,
                    quantity=payload.quantity
                )
            )

        db.commit()

        return {
            "message": "Product added to cart",
            "cart": get_cart_data(db, cart)
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not add product to cart"
        )


@router.put("/{customer_id}/items/{product_id}")
def update_cart_item(
    customer_id: int,
    product_id: int,
    payload: QuantityUpdate,
    db: Session = Depends(get_db)
):
    cart = db.query(Cart).filter(
        Cart.customer_id == customer_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if payload.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock_quantity} units available"
        )

    item.quantity = payload.quantity
    db.commit()

    return {
        "message": "Cart quantity updated",
        "cart": get_cart_data(db, cart)
    }


@router.delete("/{customer_id}/items/{product_id}")
def remove_cart_item(
    customer_id: int,
    product_id: int,
    db: Session = Depends(get_db)
):
    cart = db.query(Cart).filter(
        Cart.customer_id == customer_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Product removed from cart",
        "cart": get_cart_data(db, cart)
    }


@router.delete("/{customer_id}")
def clear_cart(
    customer_id: int,
    db: Session = Depends(get_db)
):
    cart = db.query(Cart).filter(
        Cart.customer_id == customer_id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete(synchronize_session=False)

    db.commit()

    return {
        "message": "Cart cleared successfully",
        "cart_id": cart.id
    }


