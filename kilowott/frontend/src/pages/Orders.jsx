import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Orders() {
  const [status, setStatus] = useState("");
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      setOrders(await api.orders({ status: status || undefined, limit: 300 }));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Orders</h1>
          <div className="page-sub">Track order status, totals, and product-level context.</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 18 }}>
        <div className="row" style={{ alignItems: "flex-end" }}>
          <div style={{ flex: 1 }}>
            <div className="label muted" style={{ marginBottom: 6 }}>Status</div>
            <select value={status} onChange={e => setStatus(e.target.value)}>
              <option value="">All statuses</option>
              <option value="completed">completed</option>
              <option value="processing">processing</option>
              <option value="cancelled">cancelled</option>
              <option value="refunded">refunded</option>
              <option value="failed">failed</option>
            </select>
          </div>
          <button className="btn" onClick={load}>Apply filter</button>
        </div>
      </div>

      {loading && <div className="empty">Loading orders…</div>}

      {!loading && (
        <div className="card">
          <div className="card-title">
            <h3>Order list</h3>
            <span className="muted">{orders.length} orders</span>
          </div>
          <table>
            <thead>
              <tr><th>Order</th><th>Customer</th><th>Status</th><th>Total</th><th>Date</th><th>Items</th></tr>
            </thead>
            <tbody>
              {orders.map(o => (
                <tr key={o.id}>
                  <td>#{o.wc_order_id ?? o.id}</td>
                  <td>{o.customer_id ?? "Guest"}</td>
                  <td><span className="tag">{o.status}</span></td>
                  <td>₹{Number(o.total).toLocaleString("en-IN")} {o.currency}</td>
                  <td>{new Date(o.ordered_at).toLocaleDateString()}</td>
                  <td className="muted">{o.items.map(i => `${i.product_name} (${i.category})`).join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {orders.length === 0 && <div className="empty" style={{ marginTop: 14 }}>No orders match this filter.</div>}
        </div>
      )}
    </>
  );
}