
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.categories import router as categories_router
from app.database.connection import engine, Base
from app.database import models
from app.routes.orders import router as orders_router
from app.routes.cart import router as cart_router
from app.routes.products import router as products_router
from app.routes.search import router as search_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexora Retail API")

# Allow requests from the Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(orders_router)
app.include_router(products_router)
app.include_router(search_router)
app.include_router(cart_router)
app.include_router(categories_router)


@app.get("/")
def home():
    return {"message": "Welcome to Nexora Retail API"}


@app.get("/health")
def health():
    return {"status": "healthy"}

