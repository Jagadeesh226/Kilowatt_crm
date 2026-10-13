import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useNavigate } from "react-router-dom";

function SegmentBadge({ seg }) {
  return <span className={`badge-seg seg-${seg}`}>{seg}</span>;
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);
  const [resetting, setResetting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.dashboard().then(setData).catch(e => setErr(e.message));
  }, []);

  async function reset() {
    setResetting(true);
    try {
      await api.resetDemo();
      window.location.reload();
    } finally {
      setResetting(false);
    }
  }

  if (err) return <div className="card">{err}</div>;
  if (!data) return <div className="empty">Loading dashboard…</div>;

  const t = data.totals;

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Customer Intelligence Dashboard</h1>
          <div className="page-sub">Evidence-based follow-ups, segments, and seasonal campaign context.</div>
        </div>
        <button className="btn ghost" onClick={reset} disabled={resetting}>
          {resetting ? "Resetting…" : "Reset demo data"}
        </button>
      </div>

      <div className="grid grid-4">
        <div className="card stat">
          <div className="stat-icon">👥</div>
          <span className="label">Customers</span>
          <span className="value">{t.customers}</span>
          <span className="sub">Profiles synced from demo data</span>
        </div>
        <div className="card stat">
          <div className="stat-icon">🧾</div>
          <span className="label">Eligible orders</span>
          <span className="value">{t.eligible_orders}</span>
          <span className="sub">of {t.orders} total orders</span>
        </div>
        <div className="card stat">
          <div className="stat-icon">💰</div>
          <span className="label">Eligible revenue</span>
          <span className="value">₹{t.eligible_revenue.toLocaleString("en-IN")}</span>
          <span className="sub">{t.currency} · completed / processing</span>
        </div>
        <div className="card stat">
          <div className="stat-icon">📅</div>
          <span className="label">Reference date</span>
          <span className="value" style={{ fontSize: 21 }}>{data.reference_date}</span>
          <span className="sub">Time-aware recommendation window</span>
        </div>
      </div>

      <div className="grid grid-2" style={{ marginTop: 18 }}>
        <div className="card">
          <div className="card-title"><h3>Segment overview</h3></div>
          <div className="row" style={{ gap: 16 }}>
            {Object.entries(data.segment_counts).map(([seg, n]) => (
              <div key={seg} className="tag" style={{ padding: "9px 12px", fontSize: 13 }}>
                <strong style={{ fontSize: 15 }}>{n}</strong>
                <SegmentBadge seg={seg} />
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-title">
            <h3>Follow-up queue</h3>
            <span className="muted">{data.follow_up_queue.length} customers</span>
          </div>
          {data.follow_up_queue.length === 0 ? (
            <div className="empty">No at-risk customers right now.</div>
          ) : (
            <div className="stack">
              {data.follow_up_queue.map(f => (
                <div key={f.customer_id} className="between clickable" onClick={() => navigate(`/customers/${f.customer_id}`)}>
                  <div>
                    <strong>{f.name}</strong>
                    <div className="row" style={{ gap: 6, marginTop: 4 }}>
                      <SegmentBadge seg={f.segment} />
                      <span className="muted">
                        {f.days_since_last_order} days since last order
                      </span>
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontWeight: 700 }}>₹{f.lifetime_spend.toLocaleString("en-IN")}</div>
                    <div className="muted" style={{ fontSize: 12 }}>lifetime spend</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="card" style={{ marginTop: 18 }}>
        <div className="card-title">
          <h3>Recent orders</h3>
          <span className="muted">Newest first</span>
        </div>
        <table>
          <thead>
            <tr><th>Order</th><th>Customer</th><th>Status</th><th>Total</th><th>Date</th></tr>
          </thead>
          <tbody>
            {data.recent_orders.map(o => (
              <tr key={o.id}>
                <td>#{o.wc_order_id ?? o.id}</td>
                <td>{o.customer_id ?? "Guest"}</td>
                <td><span className="tag">{o.status}</span></td>
                <td>₹{Number(o.total).toLocaleString("en-IN")} {o.currency}</td>
                <td>{new Date(o.ordered_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}