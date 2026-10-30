import { useCallback, useEffect, useState } from 'react'
import './App.css'

const money = (value) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value)

function App() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [formMessage, setFormMessage] = useState('')
  const [adjustSaving, setAdjustSaving] = useState(false)
  const [adjustMessage, setAdjustMessage] = useState('')
  const [historyProductId, setHistoryProductId] = useState(null)
  const [movements, setMovements] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')




  const loadProducts = useCallback(async (signal) => {
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/products', { signal })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      setProducts(data.products)
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError('Unable to load inventory. Check your Flask API.')
      }
    } finally {
      if (!signal?.aborted) {
        setLoading(false)
      }
    }
  }, [])

  
  useEffect(() => {
    const controller = new AbortController()

    fetch('/api/products', { signal: controller.signal })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        return response.json()
      })
      .then((data) => {
        if (!controller.signal.aborted) {
          setProducts(data.products)
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError' && !controller.signal.aborted) {
          setError('Unable to load inventory. Check your Flask API.')
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      })

    return () => controller.abort()
  }, [])


  async function handleAddProduct(event) {
    event.preventDefault()

    const form = event.currentTarget
    const formData = new FormData(form)

    const newProduct = {
      sku: String(formData.get('sku')).trim(),
      name: String(formData.get('name')).trim(),
      price: String(formData.get('price')),
      quantity: Number(formData.get('quantity')),
    }

    setSaving(true)
    setFormMessage('')

    try {
      const response = await fetch('/api/products', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newProduct),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to add product')
      }

      form.reset()
      setFormMessage('Product added successfully!')
      await loadProducts()

    } catch (err) {
      setFormMessage(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleAdjustStock(event) {
    event.preventDefault()

    const form = event.currentTarget
    const formData = new FormData(form)

    const productId = Number(formData.get('product_id'))
    const quantityChange = Number(formData.get('quantity_change'))
    const reason = String(formData.get('reason')).trim()

    if (!productId || !Number.isInteger(quantityChange) ||
        quantityChange === 0 || !reason) {
      setAdjustMessage('Please enter a valid stock adjustment.')
      return
    }

    setAdjustSaving(true)
    setAdjustMessage('')

    try {
      const response = await fetch(
        `/api/products/${productId}/adjust`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            quantity_change: quantityChange,
            reason,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Stock adjustment failed')
      }

      form.reset()
      setAdjustMessage('Stock adjusted successfully!')
      await loadProducts()

    } catch (err) {
      setAdjustMessage(err.message)
    } finally {
      setAdjustSaving(false)
    }
  }

  async function handleViewHistory(event) {
    event.preventDefault()

    const formData = new FormData(event.currentTarget)
    const productId = Number(formData.get('product_id'))

    if (!productId) {
      setHistoryError('Please select a product.')
      return
    }

    setHistoryLoading(true)
    setHistoryError('')
    setMovements([])
    setHistoryProductId(productId)

    try {
      const response = await fetch(
        `/api/products/${productId}/movements`
      )

      if (!response.ok) {
        throw new Error('Failed to retrieve transaction history')
      }

      const data = await response.json()
      setMovements(data.movements)

    } catch (err) {
      setHistoryError(err.message)
    } finally {
      setHistoryLoading(false)
    }
  }

  const totalProducts = products.length

  const totalUnits = products.reduce(
    (sum, product) => sum + product.quantity, 0
  )

  const totalValue = products.reduce(
    (sum, product) =>
      sum + Number(product.price) * product.quantity, 0
  )

  const lowStock = products.filter(
    (product) => product.quantity <= 5
  ).length

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">S</div>
          <div>
            <h2>SkyStock</h2>
            <span>Inventory Platform</span>
          </div>
        </div>

        <div className="sidebar-section">
          <p>WORKSPACE</p>
          <div className="nav-active">▦ &nbsp; Overview</div>
        </div>

        <div className="sidebar-footer">
          <div className="status-dot" />
          Local Development
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">WORKSPACE / OVERVIEW</p>
            <h1>Inventory Overview</h1>
            <p className="subtitle">
              Monitor products, stock levels, and inventory value.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={() => loadProducts()}
            disabled={loading}
          >
            ↻ Refresh
          </button>
        </header>

        <section className="stats-grid">
          <div className="stat-card">
            <p>Total Products</p>
            <h2>{totalProducts}</h2>
            <span>Products in catalog</span>
          </div>

          <div className="stat-card">
            <p>Units in Stock</p>
            <h2>{totalUnits}</h2>
            <span>Across all products</span>
          </div>

          <div className="stat-card">
            <p>Inventory Value</p>
            <h2>{money(totalValue)}</h2>
            <span>Current stock valuation</span>
          </div>

          <div className="stat-card">
            <p>Low Stock Items</p>
            <h2>{lowStock}</h2>
            <span>5 or fewer units remaining</span>
          </div>
        </section>

        <section className="inventory-panel add-product-panel">
          <div className="panel-heading">
            <div>
              <h2>Add New Product</h2>
              <p>Create a product in your inventory catalog</p>
            </div>
          </div>

          <form className="product-form" onSubmit={handleAddProduct}>
            <label>
              Product Name
              <input
                name="name"
                placeholder="e.g. Mechanical Keyboard"
                required
              />
            </label>

            <label>
              SKU
              <input
                name="sku"
                placeholder="e.g. SKY-002"
                required
              />
            </label>

            <label>
              Price ($)
              <input
                name="price"
                type="number"
                min="0"
                max="99999999.99"
                step="0.01"
                placeholder="49.99"
                required
              />
            </label>

            <label>
              Quantity
              <input
                name="quantity"
                type="number"
                min="0"
                max="2147483647"
                step="1"
                placeholder="20"
                required
              />
            </label>

            <button
              type="submit"
              className="refresh-button"
              disabled={saving}
            >
              {saving ? 'Adding...' : '+ Add Product'}
            </button>
          </form>

          {formMessage && (
            <p className="form-message" role="status">
              {formMessage}
            </p>
          )}
        </section>

        <section className="inventory-panel add-product-panel">
          <div className="panel-heading">
            <div>
              <h2>Adjust Product Stock</h2>
              <p>
                Increase or decrease inventory and record the reason.
              </p>
            </div>
          </div>

          <form className="product-form" onSubmit={handleAdjustStock}>
            <label>
              Select Product
              <select name="product_id" defaultValue="" required>
                <option value="" disabled>
                  Choose a product
                </option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} ({product.quantity} units)
                  </option>
                ))}
              </select>
            </label>

            <label>
              Quantity Change
              <input
                name="quantity_change"
                type="number"
                min="-2147483648"
                max="2147483647"
                step="1"
                placeholder="e.g. -2 or 5"
                required
              />
            </label>

            <label>
              Reason
              <input
                name="reason"
                placeholder="e.g. Customer order"
                maxLength="200"
                required
              />
            </label>

            <button
              type="submit"
              className="refresh-button"
              disabled={adjustSaving || products.length === 0}
            >
              {adjustSaving ? 'Updating...' : 'Update Stock'}
            </button>
          </form>

          {adjustMessage && (
            <p className="form-message" role="status">
              {adjustMessage}
            </p>
          )}
        </section>

        <section className="inventory-panel history-panel">
          <div className="panel-heading">
            <div>
              <h2>Stock Transaction History</h2>
              <p>
                Review inventory changes, reasons, and timestamps.
              </p>
            </div>
          </div>

          <form
            className="product-form history-form"
            onSubmit={handleViewHistory}
          >
            <label>
              Select Product
              <select name="product_id" defaultValue="" required>
                <option value="" disabled>
                  Choose a product
                </option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name}
                  </option>
                ))}
              </select>
            </label>

            <button
              type="submit"
              className="refresh-button"
              disabled={historyLoading}
            >
              {historyLoading ? 'Loading...' : 'View History'}
            </button>
          </form>

          {historyError && (
            <p className="history-error" role="alert">
              {historyError}
            </p>
          )}

          {historyProductId !== null &&
            !historyLoading &&
            !historyError && (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>TRANSACTION</th>
                      <th>CHANGE</th>
                      <th>BEFORE</th>
                      <th>AFTER</th>
                      <th>REASON</th>
                      <th>DATE</th>
                    </tr>
                  </thead>

                  <tbody>
                    {movements.map((movement) => (
                      <tr key={movement.id}>
                        <td>#{movement.id}</td>
                        <td className={
                          movement.quantity_change > 0
                            ? 'positive-change'
                            : 'negative-change'
                        }>
                          {movement.quantity_change > 0 ? '+' : ''}
                          {movement.quantity_change}
                        </td>
                        <td>{movement.quantity_before}</td>
                        <td>{movement.quantity_after}</td>
                        <td>{movement.reason}</td>
                        <td>
                          {new Date(
                            movement.created_at
                          ).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {movements.length === 0 && (
                  <p className="empty-state">
                    No stock adjustments recorded yet.
                  </p>
                )}
              </div>
            )}
        </section>

        <section className="inventory-panel">
          <div className="panel-heading">
            <div>
              <h2>Product Inventory</h2>
              <p>Live product data from PostgreSQL</p>
            </div>
            <span className="live-badge">● Connected</span>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>PRODUCT</th>
                  <th>SKU</th>
                  <th>PRICE</th>
                  <th>QUANTITY</th>
                  <th>STATUS</th>
                </tr>
              </thead>

              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td className="product-name">{product.name}</td>
                    <td>{product.sku}</td>
                    <td>{money(Number(product.price))}</td>
                    <td>{product.quantity}</td>
                    <td>
                      <span className={
                        product.quantity === 0
                          ? 'badge-out'
                          : product.quantity <= 5
                          ? 'badge-low'
                          : 'badge-good'
                      }>
                        {product.quantity === 0
                          ? 'Out of Stock'
                          : product.quantity <= 5
                          ? 'Low Stock'
                          : 'In Stock'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {!loading && !error && products.length === 0 && (
              <p className="empty-state">No products found.</p>
            )}

            {loading && <p className="empty-state">Loading inventory...</p>}
          </div>
        </section>

        <footer className="footer">
          SkyStock © 2026 • React + Flask + PostgreSQL
        </footer>
      </main>
    </div>
  )
}

export default App
