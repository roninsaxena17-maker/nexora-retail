
from collections import defaultdict

from sqlalchemy.orm import Session

from app.database.models import (
    Product,
    Customer,
    Order,
    OrderItem
)

from app.services.inventory_service import deduct_stock
from app.kafka.producer import publish_event


def create_order(
    db: Session,
    customer_id: int,
    items: list,
    delivery_address: dict
):
    if not items:
        raise ValueError("Order must contain at least one item")

    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise ValueError("Customer not found")

    # Validate delivery information.
    required_fields = [
        "delivery_name",
        "delivery_phone",
        "address_line",
        "delivery_city",
        "delivery_state",
        "postal_code"
    ]

    for field in required_fields:
        if not delivery_address.get(field):
            raise ValueError(f"{field} is required")

    # Combine duplicate product IDs.
    quantities = defaultdict(int)

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        quantities[product_id] += quantity

    order = None
    inventory_events = []

    try:
        # Validate products and capture prices.
        products = {}

        for product_id, quantity in quantities.items():
            product = (
                db.query(Product)
                .filter(Product.id == product_id)
                .first()
            )

            if not product:
                raise ValueError(
                    f"Product {product_id} not found"
                )

            if product.stock_quantity < quantity:
                raise ValueError(
                    f"Insufficient stock for {product.name}"
                )

            products[product_id] = {
                "name": product.name,
                "price": product.price
            }

        total_amount = sum(
            products[product_id]["price"] * quantity
            for product_id, quantity in quantities.items()
        )

        # Create order with delivery address.
        order = Order(
            customer_id=customer_id,
            total_amount=total_amount,
            status="placed",
            delivery_name=delivery_address["delivery_name"],
            delivery_phone=delivery_address["delivery_phone"],
            address_line=delivery_address["address_line"],
            delivery_city=delivery_address["delivery_city"],
            delivery_state=delivery_address["delivery_state"],
            postal_code=delivery_address["postal_code"],
            delivery_instructions=delivery_address.get(
                "delivery_instructions"
            )
        )

        db.add(order)
        db.flush()

        # Deduct stock and create order items.
        for product_id, quantity in quantities.items():
            product = deduct_stock(
                db,
                product_id,
                quantity
            )

            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=products[product_id]["price"]
                )
            )

            inventory_events.append({
                "product_id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "image_url": product.image_url,
                "stock_quantity": product.stock_quantity,
                "category": (
                    product.category.name
                    if product.category else None
                ),
                "city": (
                    product.city.name
                    if product.city else None
                )
            })

        db.commit()
        db.refresh(order)

    except Exception:
        db.rollback()
        raise

    # Publish events only after the database commits.
    events_published = True

    try:
        for product_data in inventory_events:
            publish_event(
                "inventory_updated",
                product_data
            )

        publish_event(
            "order_placed",
            {
                "order_id": order.id,
                "customer_id": customer_id,
                "total_amount": total_amount,
                "items": [
                    {
                        "product_id": product_id,
                        "quantity": quantity
                    }
                    for product_id, quantity in quantities.items()
                ]
            }
        )

    except Exception as error:
        events_published = False
        print(f"Order event publishing failed: {error}")

    return {
        "order_id": order.id,
        "customer_id": customer_id,
        "total_amount": total_amount,
        "status": order.status,
        "events_published": events_published,
        "delivery_address": delivery_address
    }
