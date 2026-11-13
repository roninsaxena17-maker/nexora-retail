
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.services.order_service import create_order

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class OrderItemInput(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class DeliveryAddressInput(BaseModel):
    delivery_name: str = Field(min_length=2, max_length=150)
    delivery_phone: str = Field(min_length=10, max_length=20)
    address_line: str = Field(min_length=5)
    delivery_city: str = Field(min_length=2, max_length=100)
    delivery_state: str = Field(min_length=2, max_length=100)
    postal_code: str = Field(min_length=6, max_length=10)
    delivery_instructions: str | None = None


class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[OrderItemInput] = Field(min_length=1)
    delivery_address: DeliveryAddressInput


@router.post("/", status_code=201)
def place_order(
    payload: OrderCreate,
    db: Session = Depends(get_db)
):
    try:
        result = create_order(
            db=db,
            customer_id=payload.customer_id,
            items=[
                item.model_dump()
                for item in payload.items
            ],
            delivery_address=payload.delivery_address.model_dump()
        )

        return {
            "message": "Order placed successfully",
            **result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print(f"Order creation failed: {error}")
        raise HTTPException(
            status_code=500,
            detail="Order could not be placed"
        )
