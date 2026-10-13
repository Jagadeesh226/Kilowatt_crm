import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useNavigate } from "react-router-dom";

function SegmentBadge({ seg }) {
  return <span className={`badge-seg seg-${seg}`}>{seg}</span>;
}

export default function Customers() {
  const [search, setSearch] = useState("");
  const [segment, setSegment] = useState("");
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function load() {
    setLoading(true);
    try {
      const data = await api.customers({ search, segment, limit: 200 });
      setList(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Customers</h1>
          <div className="page-sub">Search profiles, review segments, and open customer 360°.</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 18 }}>
        <div className="row" style={{ alignItems: "flex-end" }}>
          <div style={{ flex: 2 }}>
            <div className="label muted" style={{ marginBottom: 6 }}>Search</div>
            <input
              placeholder="Name, email, or phone"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <div style={{ flex: 1 }}>
            <div className="label muted" style={{ marginBottom: 6 }}>Segment</div>
            <select value={segment} onChange={e => setSegment(e.target.value)}>
              <option value="">All segments</option>
              <option value="new">new</option>
              <option value="repeat">repeat</option>
              <option value="high-value">high-value</option>
              <option value="at-risk">at-risk</option>
              <option value="inactive">inactive</option>
              <option value="active">active</option>
            </select>
          </div>
          <button className="btn" onClick={load}>Apply filters</button>
        </div>
      </div>

      {loading && <div className="empty">Loading customers…</div>}

      {!loading && (
        <div className="card">
          <div className="card-title">
            <h3>Customer list</h3>
            <span className="muted">{list.length} results</span>
          </div>
          <table>
            <thead>
              <tr><th>Name</th><th>Email</th><th>Segment</th><th>Orders</th><th>Spend</th><th>Last order</th></tr>
            </thead>
            <tbody>
              {list.map(row => (
                <tr key={row.customer.id} onClick={() => navigate(`/customers/${row.customer.id}`)} className="clickable">
                  <td>
                    <strong>{row.customer.name}</strong>
                    <div className="muted" style={{ fontSize: 12 }}>{row.customer.region || "Region unknown"}</div>
                  </td>
                  <td>{row.customer.email || "—"}</td>
                  <td><SegmentBadge seg={row.segment} /></td>
                  <td>{row.metrics.total_orders}</td>
                  <td>₹{Number(row.metrics.lifetime_spend).toLocaleString("en-IN")}</td>
                  <td>{row.metrics.days_since_last_order != null ? `${row.metrics.days_since_last_order}d ago` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {list.length === 0 && <div className="empty" style={{ marginTop: 14 }}>No customers match these filters.</div>}
        </div>
      )}
    </>
  );
}