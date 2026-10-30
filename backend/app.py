"""SkyStock's first checkpoint: verify Flask can reach PostgreSQL."""
import os
from decimal import Decimal, InvalidOperation

import psycopg
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/api/health")
def health():
    try:
        with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3) as conn:
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
            os.environ["DATABASE_URL"],
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
        with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
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

