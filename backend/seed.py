
from app.database.connection import SessionLocal
from app.database.models import Product, Category, City

db = SessionLocal()

try:
    if db.query(Product).count() > 0:
        print("Products already exist. Skipping seed.")
    else:
        electronics = Category(name="Electronics")
        fashion = Category(name="Fashion")

        bangalore = City(name="Bengaluru")
        mumbai = City(name="Mumbai")

        db.add_all([
            electronics, fashion, bangalore, mumbai
        ])
        db.flush()

        products = [
            Product(
                name="Wireless Bluetooth Headphones",
                description="Premium wireless headphones",
                price=2499,
                stock_quantity=15,
                image_url="https://placehold.co/400x400?text=Headphones",
                category_id=electronics.id,
                city_id=bangalore.id
            ),
            Product(
                name="Smart Watch Pro",
                description="Smart watch with fitness tracking",
                price=3999,
                stock_quantity=10,
                image_url="https://placehold.co/400x400?text=Smart+Watch",
                category_id=electronics.id,
                city_id=bangalore.id
            ),
            Product(
                name="Running Shoes",
                description="Lightweight running shoes",
                price=1999,
                stock_quantity=20,
                image_url="https://placehold.co/400x400?text=Shoes",
                category_id=fashion.id,
                city_id=mumbai.id
            ),
            Product(
                name="Mechanical Keyboard",
                description="RGB mechanical gaming keyboard",
                price=2999,
                stock_quantity=8,
                image_url="https://placehold.co/400x400?text=Keyboard",
                category_id=electronics.id,
                city_id=mumbai.id
            ),
            Product(
                name="USB-C Power Bank",
                description="20000mAh fast charging power bank",
                price=1799,
                stock_quantity=12,
                image_url="https://placehold.co/400x400?text=Power+Bank",
                category_id=electronics.id,
                city_id=bangalore.id
            )
        ]

        db.add_all(products)
        db.commit()

        print("5 demo products inserted successfully!")

except Exception:
    db.rollback()
    raise

finally:
    db.close()

