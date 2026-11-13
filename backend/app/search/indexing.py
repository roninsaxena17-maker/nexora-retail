from opensearchpy import helpers
from app.search.opensearch_client import client
from app.database.connection import SessionLocal
from app.database.models import Product
from sqlalchemy.orm import joinedload

INDEX_NAME = "nexora-products"


def create_product_index():
    if client.indices.exists(index=INDEX_NAME):
        print("Product index already exists.")
        return

    mapping = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        },
        "mappings": {
            "properties": {
                "product_id": {"type": "integer"},
                "name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "description": {"type": "text"},
                "price": {"type": "float"},
                "image_url": {"type": "keyword"},
                "stock_quantity": {"type": "integer"},
                "category": {"type": "keyword"},
                "city": {"type": "keyword"}
            }
        }
    }

    client.indices.create(index=INDEX_NAME, body=mapping)
    print("Nexora product index created!")


def index_all_products():
    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.city)
            )
            .all()
        )

        actions = []

        for product in products:
            document = {
                "product_id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "image_url": product.image_url,
                "stock_quantity": product.stock_quantity,
                "category": product.category.name if product.category else None,
                "city": product.city.name if product.city else None
            }

            actions.append({
                "_index": INDEX_NAME,
                "_id": str(product.id),
                "_source": document
            })

        if actions:
            helpers.bulk(client, actions)
            client.indices.refresh(index=INDEX_NAME)

        print(f"Successfully indexed {len(actions)} products!")

    finally:
        db.close()


if __name__ == "__main__":
    create_product_index()
    index_all_products()
