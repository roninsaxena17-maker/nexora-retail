from app.database.connection import SessionLocal
from app.database.models import Product

IMAGE_MAP = {
    "Wireless Bluetooth Headphones": "wireless-bluetooth-headphones.jpg",
    "Smart Watch Pro": "smart-watch-pro.jpg",
    "USB-C Power Bank": "usb-c-power-bank.jpg",
    "Nexora Premium Lipstick": "nexora-premium-lipstick.jpg",
    "Running Shoes": "running-shoes.jpg",
    "Mechanical Keyboard": "mechanical-keyboard.jpg",
    "Organic Almonds 500g": "organic-almonds-500g.jpg",
    "Basmati Rice 5kg": "basmati-rice-5kg.jpg",
    "Cold Pressed Olive Oil": "cold-pressed-olive-oil.jpg",
    "Dark Chocolate": "dark-chocolate.jpg",
    "Organic Honey 500g": "organic-honey-500g.jpg",
    "Ergonomic Office Chair": "ergonomic-office-chair.jpg",
    "Modern Study Table": "modern-study-table.jpg",
    "Three Seater Sofa": "three-seater-sofa.jpg",
    "Bedside Table": "bedside-table.jpg",
    "Bookshelf": "bookshelf.jpg",
    "Classic Cotton T-Shirt": "classic-cotton-t-shirt.jpg",
    "Slim Fit Jeans": "slim-fit-jeans.jpg",
    "Casual Hoodie": "casual-hoodie.jpg",
    "Formal Shirt": "formal-shirt.jpg",
    "Running Track Pants": "running-track-pants.jpg",
    "Nexora Matte Lipstick": "nexora-matte-lipstick.jpg",
    "Hydrating Face Serum": "hydrating-face-serum.jpg",
    "Velvet Foundation": "velvet-foundation.jpg",
    "Daily Sunscreen SPF 50": "daily-sunscreen-spf-50.jpg",
    "Premium Makeup Kit": "premium-makeup-kit.jpg",
}

def main():
    db = SessionLocal()
    updated = []
    missing = []
    try:
        for product_name, filename in IMAGE_MAP.items():
            product = (
                db.query(Product)
                .filter(Product.name == product_name)
                .one_or_none()
            )
            if product is None:
                missing.append(product_name)
                continue
            product.image_url = f"/images/products/{filename}"
            updated.append(product_name)

        if missing:
            db.rollback()
            print("No changes saved. These products were not found:")
            for name in missing:
                print(f" - {name}")
            return

        db.commit()
        print(f"Successfully updated {len(updated)} product image URLs.")
        print("No product names, prices, stock, categories, carts, or orders were changed.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
