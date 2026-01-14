from flask import Flask, request, render_template, redirect, url_for, session
from decimal import Decimal
from db import get_connection

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ===================== HELPER =====================
def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()

    conn.close()
    return product


# ===================== HOME =====================
@app.route("/")
def home():
    return redirect(url_for("login"))


# ===================== ADMIN & Customer  LOGIN =====================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 🔹 CHECK ADMIN FIRST
        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (email, password)
        )
        admin = cursor.fetchone()

        if admin:
            session.clear()
            session["admin"] = admin["id"]
            return redirect("/dashboard")

        # 🔹 CHECK CUSTOMERs
        cursor.execute(
            "SELECT * FROM customers WHERE email=%s AND password=%s",
            (email, password)
        )
        customers = cursor.fetchone()

        conn.close()

        if customers:
            session.clear()
            session["customer"] = customers["id"]
            return redirect(url_for("customer_home"))

        # ❌ INVALID LOGIN
        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")
# ===================== ADMIN DASHBOARD =====================
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))

    category = request.args.get("category")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if category:
        cursor.execute(
            "SELECT * FROM products WHERE category=%s ORDER BY updated_at DESC",
            (category,)
        )
    else:
        cursor.execute("SELECT * FROM products ORDER BY updated_at DESC")

    products = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", products=products)


# ===================== ADD PRODUCT =====================
@app.route("/add", methods=["POST"])
def add_product():
    if "admin" not in session:
        return redirect(url_for("login"))

    name = request.form["name"]
    price = request.form["price"]
    quantity = request.form["quantity"]
    unit = request.form["unit"]
    category = request.form.get("category", "General")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO products (name, price, quantity, unit, category, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """,
        (name, price, quantity, unit, category)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# ===================== EDIT PRODUCT =====================
@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        price = request.form["price"]
        quantity = request.form["quantity"]

        cursor.execute(
            """
            UPDATE products
            SET price=%s, quantity=%s, updated_at=NOW()
            WHERE id=%s
            """,
            (price, quantity, product_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    conn.close()

    return render_template("edit_product.html", product=product)


# ===================== DELETE PRODUCT =====================
@app.route("/delete/<int:product_id>")
def delete_product(product_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

# ===================== ADMIN VIEW ORDERS =====================
@app.route("/admin/orders")
def admin_orders():
    if "admin" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT o.id, o.name, o.phone, o.email, o.address,
               o.total_amount, o.created_at,
               c.name AS customer_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        ORDER BY o.created_at DESC
    """)

    orders = cursor.fetchall()
    conn.close()

    return render_template("admin_orders.html", orders=orders)



# ===================== CUSTOMER REGISTER =====================
@app.route("/customer/register", methods=["GET", "POST"])
def customer_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO customers (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        conn.commit()
        conn.close()

        return redirect("/customer/login")

    return render_template("customer_register.html")


# ===================== CUSTOMER LOGIN =====================



# ===================== CUSTOMER HOME =====================
@app.route("/customer/home")
def customer_home():
    if "customer" not in session:
        return redirect("/customer/login")

    category = request.args.get("category")
    search = request.args.get("search")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if category:
        query += " AND category=%s"
        params.append(category)

    if search:
        query += " AND name LIKE %s"
        params.append(f"%{search}%")

    cursor.execute(query, tuple(params))
    products = cursor.fetchall()
    conn.close()

    return render_template("customer_home.html", products=products)



# ===================== ADD TO CART =====================
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "customer" not in session:
        return redirect("/customer/login")

    product_id = str(request.form["product_id"])
    quantity = float(request.form["quantity"])

    cart = session.get("cart", {})

    cart[product_id] = cart.get(product_id, 0) + quantity

    session["cart"] = cart
    session.modified = True

    return redirect("/customer/home")


# ===================== VIEW CART =====================
@app.route("/cart")
def view_cart():
    if "customer" not in session:
        return redirect("/customer/login")

    cart = session.get("cart", {})
    cart_items = []
    grand_total = 0.0

    for product_id, qty in cart.items():
        product = get_product_by_id(int(product_id))

        if product:
            price = float(product["price"])
            grand_total += price * float(qty)

            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": price,
                "quantity": qty
            })

    return render_template(
        "cart.html",
        cart_items=cart_items,
        grand_total=round(grand_total, 2)
    )


# ===================== REMOVE FROM CART =====================
@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    if "customer" not in session:
        return redirect("/customer/login")

    cart = session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    session["cart"] = cart
    session.modified = True

    return redirect("/cart")
# ===================== CHECKOUT =====================
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "customer" not in session:
        return redirect("/customer/login")

    cart = session.get("cart", {})

    if not cart:
        return redirect("/customer/home")

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Calculate grand total
        grand_total = 0
        for product_id, qty in cart.items():
            cursor.execute(
                "SELECT price FROM products WHERE id=%s",
                (product_id,)
            )
            product = cursor.fetchone()
            if product:
                grand_total += float(product["price"]) * float(qty)

        # Insert order
        cursor.execute(
            """
            INSERT INTO orders
            (customer_id, name, phone, email, address, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                session["customer"],
                name,
                phone,
                email,
                address,
                grand_total
            )
        )
        order_id = cursor.lastrowid

        # Insert order items
        for product_id, qty in cart.items():
            cursor.execute(
                "SELECT price FROM products WHERE id=%s",
                (product_id,)
            )
            product = cursor.fetchone()

            if product:
                cursor.execute(
                    """
                    INSERT INTO order_items
                    (order_id, product_id, price, quantity)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        product_id,
                        product["price"],
                        qty
                    )
                )

        conn.commit()
        conn.close()

        # Clear cart
        session.pop("cart", None)

        return redirect("/order-success")

    return render_template("checkout.html")


# ===================== CUSTOMER ORDERS (STEP 17 + 19) =====================
@app.route("/orders")
def customer_orders():
    if "customer" not in session:
        return redirect("/customer/login")

    customer_id = session["customer"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, name, phone, email, address, total_amount, created_at
        FROM orders
        WHERE customer_id = %s
        ORDER BY created_at DESC
        """,
        (customer_id,)
    )

    orders = cursor.fetchall()
    conn.close()

    return render_template("orders.html", orders=orders)
#=====================ORDER SUCCES==================
@app.route("/order-success")
def order_success():
    return render_template("order_success.html")
# ===================== LOGOUT =====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ===================== RUN =====================
if __name__ == "__main__":
    app.run(debug=True)