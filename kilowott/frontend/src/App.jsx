import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import Customers from "./pages/Customers.jsx";
import CustomerDetail from "./pages/CustomerDetail.jsx";
import Orders from "./pages/Orders.jsx";
import Calendar from "./pages/Calendar.jsx";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/customers", label: "Customers" },
  { to: "/orders", label: "Orders" },
  { to: "/calendar", label: "Calendar" },
];

function Nav() {
  return (
    <header className="topbar">
      <div className="brand">
        <span className="brand-dot">◈</span>
        <span>WooCommerce CRM</span>
        <small>AI Intelligence</small>
      </div>
      <nav>
        {links.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}

export default function App() {
  return (
    <div className="app">
      <Nav />
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/customers/:id" element={<CustomerDetail />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/calendar" element={<Calendar />} />
        </Routes>
      </main>
    </div>
  );
}