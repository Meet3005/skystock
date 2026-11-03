"""SkyStock's first checkpoint: verify Flask can reach PostgreSQL."""
import os
from decimal import Decimal, InvalidOperation

import psycopg
from psycopg.conninfo import make_conninfo
from flask import Flask, jsonify, request

app = Flask(__name__)

def database_connection_string():
    local_url = os.getenv("DATABASE_URL")

    if local_url:
        return local_url

    return make_conninfo(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "skystock"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        sslmode="require",
    )



@app.get("/api/health")
def health():
    try:
        with psycopg.connect(database_connection_string(), connect_timeout=3) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                if cursor.fetchone() != (1,):
                    raise RuntimeError("Unexpected database response")
        return jsonify(app="SkyStock", status="ok", database="connected")
    except (psycopg.Error, KeyError, RuntimeError):
        # Keep connection details and passwords out of HTTP responses and logs.
        app.logger.warning("Database readiness check failed")
        return jsonify(app="SkyStock", status="unavailable", database="disconnected"), 503


@app.get("/")
def home():
    return jsonify(
        app="SkyStock",
        checkpoint="Backend and database foundation",
        next_step="Open /api/health to check the database connection",
    )

@app.get("/api/products")
def get_products():
    try:
        with psycopg.connect(
            database_connection_string(),
            connect_timeout=3
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, sku, name, price, quantity
                    FROM products
                    ORDER BY id
                    """
                )

                products = [
                    {
                        "id": row[0],
                        "sku": row[1],
                        "name": row[2],
                        "price": str(row[3]),
                        "quantity": row[4]
                    }
                    for row in cursor.fetchall()
                ]

        return jsonify(products=products), 200

    except (psycopg.Error, KeyError):
        app.logger.exception("Failed to retrieve products")
        return jsonify(error="Unable to retrieve products"), 503
    


@app.post("/api/products")
def create_product():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="A JSON object is required"), 400

    sku = data.get("sku")
    name = data.get("name")
    quantity = data.get("quantity")

    if not isinstance(sku, str) or not sku.strip():
        return jsonify(error="A valid SKU is required"), 400

    if not isinstance(name, str) or not name.strip():
        return jsonify(error="A valid product name is required"), 400

    if type(quantity) is not int or quantity < 0 or quantity > 2147483647:
        return jsonify(error="Quantity must be a nonnegative integer"), 400

    try:
        price = Decimal(str(data.get("price")))
    except (InvalidOperation, ValueError, TypeError):
        return jsonify(error="Invalid product price"), 400

    if (not price.is_finite() or price < 0
            or price > Decimal("99999999.99")
            or price.as_tuple().exponent < -2):
        return jsonify(error="Price must be nonnegative with at most two decimal places"), 400

    try:
        with psycopg.connect(database_connection_string()) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO products (sku, name, price, quantity)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, sku, name, price, quantity
                    """,
                    (sku.strip(), name.strip(), price, quantity)
                )
                row = cursor.fetchone()

        return jsonify(product={
            "id": row[0],
            "sku": row[1],
            "name": row[2],
            "price": str(row[3]),
            "quantity": row[4]
        }), 201

    except psycopg.errors.UniqueViolation:
        return jsonify(error="Product SKU already exists"), 409

    except (psycopg.Error, KeyError):
        app.logger.exception("Failed to create product")
        return jsonify(error="Unable to create product"), 503
    


@app.post("/api/products/<int:product_id>/adjust")
def adjust_product_stock(product_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="A JSON object is required"), 400

    quantity_change = data.get("quantity_change")
    reason = data.get("reason")

    if (
        type(quantity_change) is not int
        or quantity_change == 0
        or quantity_change < -2147483648
        or quantity_change > 2147483647
    ):
        return jsonify(
            error="Quantity change must be a nonzero integer"
        ), 400

    if (
        not isinstance(reason, str)
        or not reason.strip()
        or len(reason.strip()) > 200
    ):
        return jsonify(
            error="Reason must contain 1 to 200 characters"
        ), 400

    reason = reason.strip()

    try:
        with psycopg.connect(
            database_connection_string(),
            connect_timeout=3
        ) as conn:
            with conn.cursor() as cursor:

                # Lock the product row to prevent concurrent updates.
                cursor.execute(
                    """
                    SELECT quantity
                    FROM products
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (product_id,)
                )

                row = cursor.fetchone()

                if row is None:
                    return jsonify(error="Product not found"), 404

                quantity_before = row[0]
                quantity_after = quantity_before + quantity_change

                if quantity_after < 0:
                    return jsonify(error="Insufficient stock"), 409

                if quantity_after > 2147483647:
                    return jsonify(
                        error="Stock quantity exceeds maximum"
                    ), 400

                # Update the product inventory.
                cursor.execute(
                    """
                    UPDATE products
                    SET quantity = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (quantity_after, product_id)
                )

                # Record the stock movement.
                cursor.execute(
                    """
                    INSERT INTO stock_movements (
                        product_id,
                        quantity_change,
                        quantity_before,
                        quantity_after,
                        reason
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, created_at
                    """,
                    (
                        product_id,
                        quantity_change,
                        quantity_before,
                        quantity_after,
                        reason
                    )
                )

                movement_id, created_at = cursor.fetchone()

        return jsonify(movement={
            "id": movement_id,
            "product_id": product_id,
            "quantity_change": quantity_change,
            "quantity_before": quantity_before,
            "quantity_after": quantity_after,
            "reason": reason,
            "created_at": created_at.isoformat()
        }), 200

    except (psycopg.Error, KeyError):
        app.logger.exception("Failed to adjust product stock")
        return jsonify(error="Unable to adjust stock"), 503
    


@app.get("/api/products/<int:product_id>/movements")
def get_stock_movements(product_id):
    try:
        with psycopg.connect(
            database_connection_string(),
            connect_timeout=3
        ) as conn:
            with conn.cursor() as cursor:

                # Verify the product exists.
                cursor.execute(
                    "SELECT id FROM products WHERE id = %s",
                    (product_id,)
                )

                if cursor.fetchone() is None:
                    return jsonify(error="Product not found"), 404

                # Retrieve stock movements for the product.
                cursor.execute(
                    """
                    SELECT id, quantity_change,
                           quantity_before, quantity_after,
                           reason, created_at
                    FROM stock_movements
                    WHERE product_id = %s
                    ORDER BY created_at DESC, id DESC
                    """,
                    (product_id,)
                )

                movements = [
                    {
                        "id": row[0],
                        "quantity_change": row[1],
                        "quantity_before": row[2],
                        "quantity_after": row[3],
                        "reason": row[4],
                        "created_at": row[5].isoformat()
                    }
                    for row in cursor.fetchall()
                ]

        return jsonify(
            product_id=product_id,
            movements=movements
        ), 200

    except (psycopg.Error, KeyError):
        app.logger.exception("Failed to retrieve stock movements")
        return jsonify(error="Unable to retrieve movements"), 503



