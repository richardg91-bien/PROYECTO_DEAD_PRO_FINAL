import { createContext, useCallback, useContext, useEffect, useState } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

/**
 * Proveedor global de autenticación.
 * Persiste el token en localStorage y lo inyecta en cada request de axios.
 */
export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [token, setToken]     = useState(() => localStorage.getItem("access_token"));
  const [loading, setLoading] = useState(true);

  const clearSession = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    delete api.defaults.headers.common["Authorization"];
    setToken(null);
    setUser(null);
  }, []);

  // Al montar, verificar si el token guardado sigue siendo válido
  useEffect(() => {
    if (token) {
      if (token === "test-user-token") {
        setUser({ id: "test-user", email: "usuario.prueba@local" });
        setLoading(false);
        return;
      }

      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      api.get("/api/auth/me")
        .then(res => setUser(res.data))
        .catch(() => clearSession())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [clearSession, token]);

  function saveSession(accessToken, userData) {
    localStorage.setItem("access_token", accessToken);
    api.defaults.headers.common["Authorization"] = `Bearer ${accessToken}`;
    setToken(accessToken);
    setUser(userData);
  }

  async function login(email, password) {
    const res = await api.post("/api/auth/login", {
      email: email.trim().toLowerCase(),
      password,
    });
    saveSession(res.data.access_token, res.data.user);
    localStorage.setItem("refresh_token", res.data.refresh_token);
    return res.data;
  }

  async function register(email, password) {
    const res = await api.post("/api/auth/register", {
      email: email.trim().toLowerCase(),
      password,
    });
    return res.data;
  }

  function loginAsTestUser() {
    const testUser = { id: "test-user", email: "usuario.prueba@local" };
    localStorage.setItem("access_token", "test-user-token");
    api.defaults.headers.common["Authorization"] = "Bearer test-user-token";
    setToken("test-user-token");
    setUser(testUser);
  }

  async function logout() {
    try {
      await api.post("/api/auth/logout");
    } catch {
      // igual limpiamos localmente aunque falle el servidor
    } finally {
      clearSession();
    }
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, loginAsTestUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/** Hook de acceso rápido */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
