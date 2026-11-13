NEXORA PRODUCT IMAGE PACKAGE

Contents:
- frontend/public/images/products/: 26 individual square JPG product images
- backend/update_product_images.py: updates only the matching products' image_url fields

Install:
1. Extract this ZIP into the root of your existing retail_store project.
   It will merge the frontend/ and backend/ folders with your existing folders.
2. In Terminal:
   cd ~/Desktop/retail_store/backend
   source .venv/bin/activate
   python -m update_product_images
3. Refresh the frontend at http://localhost:5173

The database script updates image_url only. It does not change prices, stock,
product IDs, categories, customers, carts, or orders.
