
from app.database.connection import SessionLocal
from app.database.models import Category, Product

PRODUCTS = {
    "Beauty & Makeup": [
        ("Nexora Matte Lipstick", "Long-lasting matte lipstick", 599, 50),
        ("Hydrating Face Serum", "Vitamin C face serum", 799, 40),
        ("Velvet Foundation", "Lightweight full coverage foundation", 899, 35),
        ("Daily Sunscreen SPF 50", "Broad spectrum sun protection", 499, 60),
        ("Premium Makeup Kit", "Complete everyday makeup kit", 1499, 20),
    ],
    "Clothing": [
        ("Classic Cotton T-Shirt", "Comfortable everyday cotton T-shirt", 499, 50),
        ("Slim Fit Jeans", "Modern slim fit denim jeans", 1299, 30),
        ("Casual Hoodie", "Soft fleece casual hoodie", 999, 25),
        ("Formal Shirt", "Premium office wear shirt", 899, 35),
        ("Running Track Pants", "Lightweight sports track pants", 699, 40),
    ],
    "Furniture": [
        ("Ergonomic Office Chair", "Adjustable chair with lumbar support", 5999, 12),
        ("Modern Study Table", "Minimal wooden study table", 4499, 10),
        ("Three Seater Sofa", "Comfortable modern living room sofa", 18999, 5),
        ("Bedside Table", "Compact wooden bedside table", 1999, 15),
        ("Bookshelf", "Five shelf storage bookshelf", 3499, 8),
    ],
    "Food & Groceries": [
        ("Organic Almonds 500g", "Premium quality whole almonds", 499, 40),
        ("Basmati Rice 5kg", "Premium long grain basmati rice", 699, 30),
        ("Cold Pressed Olive Oil", "Extra virgin olive oil 500ml", 599, 25),
        ("Dark Chocolate", "Premium dark chocolate 100g", 199, 60),
        ("Organic Honey 500g", "Natural unprocessed honey", 349, 35),
    ],
}


def seed_products():
    db = SessionLocal()

    try:
        added = 0
        skipped = 0

        for category_name, products in PRODUCTS.items():
            category = (
                db.query(Category)
                .filter(Category.name == category_name)
                .first()
            )

            if not category:
                category = Category(name=category_name)
                db.add(category)
                db.flush()

            for name, description, price, stock in products:
                existing = (
                    db.query(Product)
                    .filter(
                        Product.name == name,
                        Product.category_id == category.id
                    )
                    .first()
                )

                if existing:
                    skipped += 1
                    continue

                product = Product(
                    name=name,
                    description=description,
                    price=price,
                    image_url=(
                        "https://placehold.co/400x400"
                        f"?text={name.replace(' ', '+')}"
                    ),
                    stock_quantity=stock,
                    category_id=category.id,
                    city_id=None,
                )

                db.add(product)
                added += 1

        db.commit()

        print("\n========== NEXORA SEED COMPLETE ==========")
        print(f"Products added: {added}")
        print(f"Products skipped: {skipped}")
        print(f"Total products in database: {db.query(Product).count()}")
        print("==========================================")

    except Exception as error:
        db.rollback()
        print("Seeding failed:", error)
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_products()

