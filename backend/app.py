"""SkyStock's first checkpoint: verify Flask can reach PostgreSQL."""
import os

import psycopg
from flask import Flask, jsonify

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
