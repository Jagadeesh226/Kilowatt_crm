import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Calendar() {
  const [camps, setCamps] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.campaigns().then(setCamps).finally(() => setLoading(false));
  }, []);

  const today = new Date().toISOString().slice(0, 10);

  function leadStart(c) {
    const d = new Date(c.start_date);
    d.setDate(d.getDate() - c.lead_days);
    return d.toISOString().slice(0, 10);
  }

  function isActive(c) {
    return leadStart(c) <= today && today <= c.end_date;
  }

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Seasonal campaign calendar</h1>
          <div className="page-sub">Configured festival windows, lead times, and eligible categories.</div>
        </div>
      </div>

      {loading && <div className="empty">Loading calendar…</div>}

      {!loading && (
        <div className="grid grid-3">
          {camps.map(c => (
            <div className={`card ${isActive(c) ? "insight" : ""}`} key={c.id}>
              <div className="card-title">
                <h3>{c.name}</h3>
                <span className={`badge-seg ${isActive(c) ? "seg-repeat" : "seg-inactive"}`}>
                  {isActive(c) ? "Active window" : "Inactive"}
                </span>
              </div>

              <div className="kv"><span className="k">Campaign dates</span><span>{c.start_date} → {c.end_date}</span></div>
              <div className="kv"><span className="k">Lead time</span><span>{c.lead_days} days</span></div>
              <div className="kv"><span className="k">Outreach starts</span><span>{leadStart(c)}</span></div>
              <div className="kv"><span className="k">Region</span><span>{c.region || "Any"}</span></div>

              <div style={{ marginTop: 12 }}>
                <div className="muted" style={{ marginBottom: 6 }}>Eligible categories</div>
                {(c.eligible_categories || []).map(cat => <span className="tag" key={cat}>{cat}</span>)}
              </div>

              {c.notes && <div className="muted" style={{ marginTop: 12 }}>{c.notes}</div>}
            </div>
          ))}
        </div>
      )}
    </>
  );
}