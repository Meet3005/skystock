
CREATE TABLE IF NOT EXISTS stock_movements (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES products(id),
    quantity_change INTEGER NOT NULL CHECK (quantity_change <> 0),
    quantity_before INTEGER NOT NULL CHECK (quantity_before >= 0),
    quantity_after INTEGER NOT NULL CHECK (quantity_after >= 0),
    reason TEXT NOT NULL CHECK (TRIM(reason) <> ''),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (
        quantity_after::BIGINT =
        quantity_before::BIGINT + quantity_change::BIGINT
    )
);
