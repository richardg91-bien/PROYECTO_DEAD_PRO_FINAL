import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <div className="p-8">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>Dashboard</h1>
          {user && <p style={{ color: "#888", fontSize: 14 }}>Bienvenido, {user.email}</p>}
        </div>
        <button onClick={handleLogout} className="auth-btn" style={{ width: "auto", padding: "0.5rem 1.2rem" }}>
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}
