import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api.js";

function SegmentBadge({ seg }) {
  return <span className={`badge-seg seg-${seg}`}>{seg}</span>;
}

export default function CustomerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [cust, setCust] = useState(null);
  const [orders, setOrders] = useState([]);
  const [rec, setRec] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState("");
  const [copying, setCopying] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const [c, o] = await Promise.all([
        api.customer(id),
        api.customerOrders(id),
      ]);
      setCust(c);
      setOrders(o);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [id]);

  async function generate() {
    setGenerating(true);
    try {
      const r = await api.recommend(id);
      setRec(r);
      setMessage(r.ai?.message_draft || "");
    } finally {
      setGenerating(false);
    }
  }

  async function copy() {
    setCopying(true);
    try {
      await navigator.clipboard.writeText(message);
      setTimeout(() => setCopying(false), 1200);
    } catch {
      setCopying(false);
    }
  }

  function confClass(c) {
    if (!c) return "";
    if (c.startsWith("high")) return "conf-high";
    if (c.startsWith("medium")) return "conf-medium";
    return "conf-low";
  }

  if (loading) return <div className="empty">Loading customer profile…</div>;
  if (!cust) return <div className="card">Customer not found.</div>;

  const m = cust.metrics;

  return (
    <>
      <button className="btn ghost small" onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Back
      </button>

      <div className="page-head">
        <div>
          <h1>{cust.customer.name}</h1>
          <div className="page-sub">
            {cust.customer.email || "No email"} · {cust.customer.phone || "No phone"} · {cust.customer.region || "Region unknown"}
          </div>
        </div>
        <SegmentBadge seg={cust.segment} />
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-title"><h3>Profile & metrics</h3></div>
          <div className="kv"><span className="k">Segment</span><span>{cust.segment}</span></div>
          <div className="kv"><span className="k">Why this segment</span><span>{cust.segment_reasons.join("; ")}</span></div>
          <div className="kv"><span className="k">Total orders</span><span>{m.total_orders}</span></div>
          <div className="kv"><span className="k">Lifetime spend</span><span>₹{Number(m.lifetime_spend).toLocaleString("en-IN")}</span></div>
          <div className="kv"><span className="k">Average order</span><span>₹{Number(m.average_order_value).toLocaleString("en-IN")}</span></div>
          <div className="kv"><span className="k">Last order</span><span>{m.last_order_date ? new Date(m.last_order_date).toLocaleDateString() : "—"}</span></div>
          <div className="kv"><span className="k">Days since</span><span>{m.days_since_last_order ?? "—"}</span></div>
          <div className="kv"><span className="k">Marketing consent</span><span>{cust.customer.marketing_consent ? "Yes" : "No"}</span></div>
          <div style={{ marginTop: 12 }}>
            <div className="muted" style={{ marginBottom: 6 }}>Top categories</div>
            {m.top_categories.length === 0 && <span className="muted">No purchase evidence.</span>}
            {m.top_categories.map(tc => (
              <span className="tag" key={tc.category}>{tc.category} · {tc.quantity}</span>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-title">
            <h3>Order history</h3>
            <span className="muted">{orders.length} orders</span>
          </div>
          <div className="timeline">
            {orders.map(o => (
              <div className="timeline-item" key={o.id}>
                <div className="between">
                  <strong>Order #{o.wc_order_id ?? o.id}</strong>
                  <span className="muted">{new Date(o.ordered_at).toLocaleDateString()}</span>
                </div>
                <div className="muted" style={{ marginTop: 3 }}>
                  {o.status} · ₹{Number(o.total).toLocaleString("en-IN")} {o.currency}
                </div>
                <div style={{ marginTop: 6 }}>
                  {o.items.map(i => (
                    <span className="tag" key={i.id}>{i.product_name} · {i.category} ×{i.quantity}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
          {orders.length === 0 && <div className="empty">No orders available.</div>}
        </div>
      </div>

      <div className="card insight" style={{ marginTop: 18 }}>
        <div className="card-title">
          <h3>AI next-best action</h3>
          <button className="btn" onClick={generate} disabled={generating}>
            {generating ? "Generating…" : rec ? "Regenerate" : "Generate recommendation"}
          </button>
        </div>

        {!rec && <div className="empty">Generate an evidence-based recommendation for this customer.</div>}

        {rec && (
          <div className="stack">
            <div className="grid grid-3">
              <div className="card stat" style={{ minHeight: 0 }}>
                <span className="label">Candidate</span>
                <span style={{ fontSize: 18, fontWeight: 700 }}>{rec.candidate_category || "No outreach"}</span>
              </div>
              <div className="card stat" style={{ minHeight: 0 }}>
                <span className="label">Confidence</span>
                <span style={{ fontSize: 18, fontWeight: 700 }} className={confClass(rec.confidence)}>
                  {rec.confidence || "—"}
                </span>
              </div>
              <div className="card stat" style={{ minHeight: 0 }}>
                <span className="label">Campaign</span>
                <span style={{ fontSize: 18, fontWeight: 700 }}>
                  {rec.selected_campaign?.name || "None active"}
                </span>
              </div>
            </div>

            {rec.suppressed && (
              <div className="card" style={{ borderColor: "rgba(251, 113, 133, 0.55)" }}>
                <strong>Suppressed:</strong> {rec.suppression_reasons.join("; ")}
              </div>
            )}

            <div>
              <div className="muted" style={{ marginBottom: 6 }}>Why this customer, why now</div>
              <ul style={{ margin: 0, paddingLeft: 18 }}>
                {rec.reasons.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>

            {rec.evidence?.length > 0 && (
              <div>
                <div className="muted" style={{ marginBottom: 6 }}>Evidence from order history</div>
                <table>
                  <thead>
                    <tr><th>Order</th><th>Date</th><th>Status</th><th>Categories</th></tr>
                  </thead>
                  <tbody>
                    {rec.evidence.map(e => (
                      <tr key={e.order_id}>
                        <td>#{e.wc_order_id ?? e.order_id}</td>
                        <td>{e.ordered_at}</td>
                        <td><span className="tag">{e.status}</span></td>
                        <td>{(e.categories || []).join(", ")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {rec.active_campaigns?.length > 0 && (
              <div>
                <div className="muted" style={{ marginBottom: 6 }}>Active campaigns</div>
                {rec.active_campaigns.map(c => <span className="tag" key={c.id}>{c.name}</span>)}
              </div>
            )}

            <div className="ai-panel">
              <div className="ai-head">AI explanation · {rec.ai?.source}</div>
              <p style={{ margin: 0 }}>{rec.ai?.explanation}</p>
              {rec.ai?.confidence_note && <div className="muted" style={{ marginTop: 8 }}>{rec.ai.confidence_note}</div>}
            </div>

            <div>
              <div className="between" style={{ marginBottom: 8 }}>
                <span className="muted">Suggested message</span>
                <button className="btn ghost small" onClick={copy}>
                  {copying ? "Copied!" : "Copy message"}
                </button>
              </div>
              <div className="card" style={{ padding: 12, marginBottom: 10 }}>
                <div className="muted" style={{ fontSize: 12, marginBottom: 4 }}>Subject</div>
                <div>{rec.ai?.suggested_subject || "No subject"}</div>
              </div>
              <textarea value={message} onChange={e => setMessage(e.target.value)} />
            </div>
          </div>
        )}
      </div>
    </>
  );
}