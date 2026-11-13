
import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  Search, ShoppingCart, UserRound, MapPin, Menu, Heart,
  ArrowRight, Plus, Minus, X, Sparkles, Truck,
  ShieldCheck, Headphones, CheckCircle2, Package
} from "lucide-react";
import HeroScene from "./components/HeroScene";
import "./index.css";

const API = "http://127.0.0.1:8000";
const CUSTOMER_ID = 1;

const categories = [
  { name: "All", icon: "✦" },
  { name: "Beauty & Makeup", icon: "💄" },
  { name: "Clothing", icon: "👕" },
  { name: "Furniture", icon: "🛋️" },
  { name: "Food & Groceries", icon: "🥑" },
];

const categoryCards = [
  {
    name: "Beauty & Makeup",
    subtitle: "A little self-care goes a long way",
    image: "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=700",
  },
  {
    name: "Clothing",
    subtitle: "Your style, your story",
    image: "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=700",
  },
  {
    name: "Furniture",
    subtitle: "Make room for better living",
    image: "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=700",
  },
  {
    name: "Food & Groceries",
    subtitle: "Fresh picks for every day",
    image: "https://images.unsplash.com/photo-1542838132-92c53300491e?w=700",
  },
];

const emptyAddress = {
  delivery_name: "",
  delivery_phone: "",
  address_line: "",
  delivery_city: "",
  delivery_state: "",
  postal_code: "",
  delivery_instructions: "",
};

function App() {
  const [products, setProducts] = useState([]);
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");
  const [cart, setCart] = useState([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [cartLoading, setCartLoading] = useState(false);
  const [notice, setNotice] = useState("");

  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [address, setAddress] = useState(emptyAddress);
  const [orderSuccess, setOrderSuccess] = useState(null);

  const showNotice = (message) => {
    setNotice(message);
    setTimeout(() => setNotice(""), 3000);
  };

  const syncCart = (cartData) => {
    if (!cartData || !Array.isArray(cartData.items)) return;

    setCart(
      cartData.items.map((item) => ({
        id: item.product_id,
        name: item.name,
        price: Number(item.price),
        image_url: item.image_url,
        quantity: item.quantity,
        available_stock: item.available_stock,
      }))
    );
  };

  const loadCart = async () => {
    const response = await axios.get(`${API}/cart/${CUSTOMER_ID}`);
    syncCart(response.data);
  };

  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await axios.get(`${API}/products/`);

        if (Array.isArray(response.data)) {
          setProducts(
            response.data.map((product) => ({
              ...product,
              id: product.id ?? product.product_id,
            }))
          );
        }
      } catch (error) {
        console.error("Product loading error:", error);
        showNotice("Could not load products");
      } finally {
        setLoading(false);
      }

      try {
        await loadCart();
      } catch (error) {
        console.error("Cart loading error:", error);
      }
    };

    loadData();
  }, []);

  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      const matchesCategory =
        activeCategory === "All" ||
        product.category === activeCategory;

      const term = search.toLowerCase();

      const matchesSearch =
        (product.name || "").toLowerCase().includes(term) ||
        (product.description || "").toLowerCase().includes(term);

      return matchesCategory && matchesSearch;
    });
  }, [products, activeCategory, search]);

  const addToCart = async (product) => {
    try {
      setCartLoading(true);

      const response = await axios.post(
        `${API}/cart/${CUSTOMER_ID}/items`,
        {
          product_id: product.id ?? product.product_id,
          quantity: 1,
        }
      );

      syncCart(response.data.cart);
      showNotice("Added to your cart");
    } catch (error) {
      console.error("Add to cart error:", error);
      showNotice(
        error.response?.data?.detail || "Could not add product"
      );
    } finally {
      setCartLoading(false);
    }
  };

  const updateQuantity = async (productId, change) => {
    const item = cart.find((entry) => entry.id === productId);
    if (!item) return;

    const newQuantity = item.quantity + change;

    try {
      setCartLoading(true);

      let response;

      if (newQuantity <= 0) {
        response = await axios.delete(
          `${API}/cart/${CUSTOMER_ID}/items/${productId}`
        );
      } else {
        response = await axios.put(
          `${API}/cart/${CUSTOMER_ID}/items/${productId}`,
          { quantity: newQuantity }
        );
      }

      syncCart(response.data.cart);
    } catch (error) {
      console.error("Quantity update error:", error);
      showNotice(
        error.response?.data?.detail || "Could not update cart"
      );
    } finally {
      setCartLoading(false);
    }
  };

  const removeFromCart = async (productId) => {
    try {
      setCartLoading(true);

      const response = await axios.delete(
        `${API}/cart/${CUSTOMER_ID}/items/${productId}`
      );

      syncCart(response.data.cart);
      showNotice("Product removed");
    } catch (error) {
      console.error("Remove error:", error);
      showNotice("Could not remove product");
    } finally {
      setCartLoading(false);
    }
  };

  const cartCount = cart.reduce(
    (sum, item) => sum + item.quantity,
    0
  );

  const cartTotal = cart.reduce(
    (sum, item) => sum + Number(item.price) * item.quantity,
    0
  );

  const openCheckout = () => {
    if (cart.length === 0) {
      showNotice("Your cart is empty");
      return;
    }

    setCartOpen(false);
    setCheckoutOpen(true);
  };

  const updateAddress = (event) => {
    const { name, value } = event.target;

    setAddress((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const placeOrder = async (event) => {
    event.preventDefault();

    if (cart.length === 0) {
      showNotice("Your cart is empty");
      return;
    }

    try {
      setCheckoutLoading(true);

      const payload = {
        customer_id: CUSTOMER_ID,
        items: cart.map((item) => ({
          product_id: item.id,
          quantity: item.quantity,
        })),
        delivery_address: {
          ...address,
          delivery_name: address.delivery_name.trim(),
          delivery_phone: address.delivery_phone.trim(),
          address_line: address.address_line.trim(),
          delivery_city: address.delivery_city.trim(),
          delivery_state: address.delivery_state.trim(),
          postal_code: address.postal_code.trim(),
          delivery_instructions:
            address.delivery_instructions.trim() || null,
        },
      };

      const response = await axios.post(
        `${API}/orders/`,
        payload
      );

      const order = response.data;

      setCart([]);

      try {
        await axios.delete(`${API}/cart/${CUSTOMER_ID}`);
      } catch (clearError) {
        console.error("Cart clearing error:", clearError);
      }

      setCheckoutOpen(false);
      setCartOpen(false);
      setAddress(emptyAddress);
      setOrderSuccess(order);
    } catch (error) {
      console.error("Order placement error:", error);

      showNotice(
        error.response?.data?.detail ||
        "Order could not be placed. Please try again."
      );
    } finally {
      setCheckoutLoading(false);
    }
  };

  const selectCategory = (name) => {
    setActiveCategory(name);
    document.getElementById("products")?.scrollIntoView({
      behavior: "smooth",
    });
  };

  return (
    <div className="app">

      {/* ANNOUNCEMENT */}
      <div className="announcement">
        <Sparkles size={14} />
        <span>Thoughtfully chosen. Delivered to your door.</span>
        <span className="announcement-right">
          FREE DELIVERY ON ORDERS ABOVE ₹999
        </span>
      </div>

      {/* HEADER */}
      <header className="header">
        <div className="header-main">

          <button className="icon-button mobile-menu" aria-label="Menu">
            <Menu />
          </button>

          <a className="brand" href="#">
            <span className="brand-mark">N</span>
            <span>NEXORA<span className="brand-light">.</span></span>
          </a>

          <div className="delivery">
            <MapPin size={17} />
            <div>
              <small>Delivering to</small>
              <strong>Bengaluru 560001</strong>
            </div>
          </div>

          <form
            className="search-box"
            onSubmit={(event) => event.preventDefault()}
          >
            <Search size={19} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search for anything..."
            />

            {search && (
              <button type="button" onClick={() => setSearch("")}>
                <X size={16} />
              </button>
            )}

            <button className="search-submit" type="submit">
              Search
            </button>
          </form>

          <button className="account-button">
            <UserRound size={20} />
            <span>
              <small>Welcome</small>
              <strong>My Account</strong>
            </span>
          </button>

          <button
            className="cart-button"
            onClick={() => setCartOpen(true)}
          >
            <ShoppingCart size={23} />
            <span className="cart-count">{cartCount}</span>
            <strong>Cart</strong>
          </button>
        </div>

        <nav className="category-nav">
          <span className="nav-label">EXPLORE</span>

          {categories.slice(1).map((category) => (
            <button
              key={category.name}
              className={
                activeCategory === category.name ? "nav-active" : ""
              }
              onClick={() => selectCategory(category.name)}
            >
              {category.icon} {category.name}
            </button>
          ))}

          <span className="nav-spacer" />
          <span className="nav-tag">A little more, every day.</span>
        </nav>
      </header>

      <main>

        {/* NEW IMMERSIVE 3D HERO */}
        <section className="hero">
          <div className="hero-content">
            <span className="eyebrow">
              <Sparkles size={15} /> THE NEXORA EDIT
            </span>

            <h1>
              Everything you love.
              <br />
              <em>One place.</em>
            </h1>

            <p>
              Discover everyday essentials, thoughtful finds and little
              luxuries across the things that make life better.
            </p>

            <button
              className="primary-button"
              onClick={() => {
                setActiveCategory("All");
                document.getElementById("products")?.scrollIntoView({
                  behavior: "smooth",
                });
              }}
            >
              Explore the collection <ArrowRight size={17} />
            </button>

            <div className="hero-note">
              CURATED FOR YOUR EVERYDAY
            </div>
          </div>

          <div className="hero-visual">
            <div className="hero-visual-glow" />

            <HeroScene />

            <div className="hero-floating-card">
              <span>✳ THE NEXORA EDIT</span>
              <strong>Not just shopping.</strong>
              <small>A whole new way to discover.</small>
            </div>

            <div className="hero-visual-index">
              01 / 04
            </div>
          </div>
        </section>

        {/* BENEFITS */}
        <section className="benefits">
          <div>
            <Truck />
            <span>
              <strong>Free delivery</strong>
              <small>On orders above ₹999</small>
            </span>
          </div>

          <div>
            <ShieldCheck />
            <span>
              <strong>Secure shopping</strong>
              <small>Your data stays protected</small>
            </span>
          </div>

          <div>
            <Headphones />
            <span>
              <strong>Here to help</strong>
              <small>Customer-first support</small>
            </span>
          </div>
        </section>

        {/* CATEGORIES */}
        <section className="category-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">EXPLORE BY CATEGORY</span>
              <h2>
                Find your kind of <em>good.</em>
              </h2>
            </div>

            <span className="muted">
              A world of everyday favourites
            </span>
          </div>

          <div className="category-grid">
            {categoryCards.map((category) => (
              <button
                className="category-card"
                key={category.name}
                onClick={() => selectCategory(category.name)}
              >
                <img src={category.image} alt={category.name} />

                <div className="category-overlay">
                  <span>{category.subtitle}</span>
                  <strong>{category.name}</strong>
                  <span className="category-link">
                    Explore <ArrowRight size={15} />
                  </span>
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* PRODUCTS */}
        <section className="products-section" id="products">
          <div className="section-heading product-heading">
            <div>
              <span className="eyebrow">HANDPICKED FOR YOU</span>
              <h2>
                {activeCategory === "All"
                  ? "The latest finds"
                  : activeCategory}
              </h2>
            </div>

            <div className="product-filters">
              {categories.map((category) => (
                <button
                  key={category.name}
                  className={
                    activeCategory === category.name
                      ? "filter-active"
                      : ""
                  }
                  onClick={() => setActiveCategory(category.name)}
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>

          {loading && (
            <p className="loading-text">Loading products...</p>
          )}

          <div className="product-grid">
            {filteredProducts.map((product) => (
              <article className="product-card" key={product.id}>
                <div className="product-image">
                  <img
                    src={product.image_url || ""}
                    alt={product.name}
                  />

                  <button
                    className="wishlist"
                    aria-label="Add to wishlist"
                  >
                    <Heart size={18} />
                  </button>

                  <button
                    className="quick-add"
                    disabled={cartLoading}
                    onClick={() => addToCart(product)}
                  >
                    <Plus size={17} /> Add to cart
                  </button>
                </div>

                <div className="product-info">
                  <span className="product-category">
                    {product.category || "NEXORA PICK"}
                  </span>

                  <h3>{product.name}</h3>

                  <p>
                    {product.description ||
                      "A little something for your everyday."}
                  </p>

                  <div className="product-bottom">
                    <strong>
                      ₹{Number(product.price).toLocaleString("en-IN")}
                    </strong>

                    <button
                      disabled={cartLoading}
                      onClick={() => addToCart(product)}
                      aria-label="Add to cart"
                    >
                      <Plus size={18} />
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>

          {!loading && filteredProducts.length === 0 && (
            <div className="empty-products">
              <Search size={30} />
              <h3>No products found</h3>
              <p>
                Try another search or explore a different category.
              </p>

              <button
                onClick={() => {
                  setSearch("");
                  setActiveCategory("All");
                }}
              >
                Show all products
              </button>
            </div>
          )}
        </section>

        {/* NEWSLETTER */}
        <section className="newsletter">
          <div>
            <span className="eyebrow">A GOOD THING, NOW AND THEN</span>
            <h2>
              Stay in the <em>know.</em>
            </h2>
            <p>
              New finds, thoughtful picks and a little inspiration
              in your inbox.
            </p>
          </div>

          <form
            onSubmit={(event) => {
              event.preventDefault();
              showNotice("Thanks for joining Nexora!");
            }}
          >
            <input
              type="email"
              placeholder="Your email address"
              required
            />
            <button type="submit">
              Join us <ArrowRight size={16} />
            </button>
          </form>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="footer">
        <a className="brand footer-brand" href="#">
          <span className="brand-mark">N</span>
          <span>NEXORA<span className="brand-light">.</span></span>
        </a>

        <p>Thoughtfully chosen. Made for everyday.</p>
        <span>© 2026 Nexora Retail</span>
      </footer>

      {notice && <div className="toast">{notice}</div>}

      {/* SHOPPING CART */}
      {cartOpen && (
        <div
          className="cart-backdrop"
          onClick={() => setCartOpen(false)}
        >
          <aside
            className="cart-drawer"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="cart-header">
              <div>
                <span className="eyebrow">YOUR BAG</span>
                <h2>Shopping cart ({cartCount})</h2>
              </div>

              <button onClick={() => setCartOpen(false)}>
                <X />
              </button>
            </div>

            {cart.length === 0 ? (
              <div className="empty-cart">
                <ShoppingCart size={42} />
                <h3>Your cart is waiting</h3>
                <p>Looks like you haven't added anything yet.</p>

                <button
                  className="primary-button"
                  onClick={() => setCartOpen(false)}
                >
                  Start exploring
                </button>
              </div>
            ) : (
              <>
                <div className="cart-items">
                  {cart.map((item) => (
                    <div className="cart-item" key={item.id}>
                      <img
                        src={item.image_url || ""}
                        alt={item.name}
                      />

                      <div className="cart-item-info">
                        <strong>{item.name}</strong>

                        <span>
                          ₹{Number(item.price).toLocaleString("en-IN")}
                        </span>

                        <div className="quantity-control">
                          <button
                            disabled={cartLoading}
                            onClick={() => updateQuantity(item.id, -1)}
                          >
                            <Minus size={14} />
                          </button>

                          <span>{item.quantity}</span>

                          <button
                            disabled={cartLoading}
                            onClick={() => updateQuantity(item.id, 1)}
                          >
                            <Plus size={14} />
                          </button>
                        </div>

                        <button
                          className="remove-item"
                          onClick={() => removeFromCart(item.id)}
                          disabled={cartLoading}
                        >
                          Remove
                        </button>
                      </div>

                      <strong>
                        ₹{(
                          Number(item.price) * item.quantity
                        ).toLocaleString("en-IN")}
                      </strong>
                    </div>
                  ))}
                </div>

                <div className="cart-footer">
                  <div>
                    <span>Subtotal</span>
                    <strong>
                      ₹{cartTotal.toLocaleString("en-IN")}
                    </strong>
                  </div>

                  <small>
                    Final total is calculated by the server when you place
                    your order.
                  </small>

                  <button
                    className="primary-button"
                    onClick={openCheckout}
                    disabled={cartLoading}
                  >
                    Continue to checkout <ArrowRight size={17} />
                  </button>
                </div>
              </>
            )}
          </aside>
        </div>
      )}

      {/* CHECKOUT */}
      {checkoutOpen && (
        <div className="cart-backdrop checkout-backdrop">
          <section className="checkout-panel">
            <div className="cart-header">
              <div>
                <span className="eyebrow">NEXORA CHECKOUT</span>
                <h2>Delivery details</h2>
              </div>

              <button
                onClick={() => setCheckoutOpen(false)}
                disabled={checkoutLoading}
              >
                <X />
              </button>
            </div>

            <div className="checkout-content">
              <form onSubmit={placeOrder}>
                <h3>Where should we deliver?</h3>

                <label>
                  Full name
                  <input
                    name="delivery_name"
                    value={address.delivery_name}
                    onChange={updateAddress}
                    placeholder="Your full name"
                    minLength={2}
                    maxLength={150}
                    required
                  />
                </label>

                <label>
                  Phone number
                  <input
                    name="delivery_phone"
                    value={address.delivery_phone}
                    onChange={updateAddress}
                    placeholder="10-digit mobile number"
                    type="tel"
                    minLength={10}
                    maxLength={20}
                    pattern="[0-9+ -]{10,20}"
                    required
                  />
                </label>

                <label>
                  House number, street and area
                  <textarea
                    name="address_line"
                    value={address.address_line}
                    onChange={updateAddress}
                    placeholder="Flat, building, street, locality"
                    minLength={5}
                    required
                    rows={3}
                  />
                </label>

                <div className="checkout-two-columns">
                  <label>
                    City
                    <input
                      name="delivery_city"
                      value={address.delivery_city}
                      onChange={updateAddress}
                      placeholder="Bengaluru"
                      required
                    />
                  </label>

                  <label>
                    State
                    <input
                      name="delivery_state"
                      value={address.delivery_state}
                      onChange={updateAddress}
                      placeholder="Karnataka"
                      required
                    />
                  </label>
                </div>

                <label>
                  PIN code
                  <input
                    name="postal_code"
                    value={address.postal_code}
                    onChange={updateAddress}
                    placeholder="6-digit PIN code"
                    inputMode="numeric"
                    pattern="[0-9]{6,10}"
                    minLength={6}
                    maxLength={10}
                    required
                  />
                </label>

                <label>
                  Delivery instructions (optional)
                  <textarea
                    name="delivery_instructions"
                    value={address.delivery_instructions}
                    onChange={updateAddress}
                    placeholder="Any directions for the delivery partner?"
                    rows={2}
                  />
                </label>

                <div className="checkout-payment-note">
                  <Package size={20} />
                  <div>
                    <strong>Cash on Delivery / Test Order</strong>
                    <small>
                      No online payment will be collected in this test flow.
                    </small>
                  </div>
                </div>

                <button
                  className="primary-button checkout-submit"
                  type="submit"
                  disabled={checkoutLoading || cart.length === 0}
                >
                  {checkoutLoading
                    ? "Placing your order..."
                    : "Place order"}
                  {!checkoutLoading && <ArrowRight size={17} />}
                </button>
              </form>

              <aside className="checkout-summary">
                <h3>Order summary</h3>

                {cart.map((item) => (
                  <div className="checkout-summary-item" key={item.id}>
                    <span>
                      {item.name} × {item.quantity}
                    </span>

                    <strong>
                      ₹{(
                        Number(item.price) * item.quantity
                      ).toLocaleString("en-IN")}
                    </strong>
                  </div>
                ))}

                <div className="checkout-summary-total">
                  <span>Estimated subtotal</span>
                  <strong>
                    ₹{cartTotal.toLocaleString("en-IN")}
                  </strong>
                </div>

                <small>
                  The backend calculates the final order total using
                  current database prices.
                </small>
              </aside>
            </div>
          </section>
        </div>
      )}

      {/* ORDER SUCCESS */}
      {orderSuccess && (
        <div className="cart-backdrop">
          <section className="order-success">
            <CheckCircle2 size={58} />

            <span className="eyebrow">ORDER CONFIRMED</span>
            <h2>Your order is placed!</h2>

            <p>
              Thank you for shopping with Nexora. Your order has been
              saved successfully.
            </p>

            <div className="success-order-number">
              <span>Order ID</span>
              <strong>#{orderSuccess.order_id}</strong>
            </div>

            <div className="success-order-number">
              <span>Order total</span>
              <strong>
                ₹{Number(orderSuccess.total_amount).toLocaleString("en-IN")}
              </strong>
            </div>

            <div className="success-order-number">
              <span>Status</span>
              <strong>{orderSuccess.status}</strong>
            </div>

            <button
              className="primary-button"
              onClick={() => setOrderSuccess(null)}
            >
              Continue shopping <ArrowRight size={17} />
            </button>
          </section>
        </div>
      )}

    </div>
  );
}

export default App;
