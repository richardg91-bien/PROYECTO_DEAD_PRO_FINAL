import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider } from "../context/AuthContext";
import PrivateRoute    from "./PrivateRoute";

import Welcome   from "../pages/Welcome";
import Home      from "../pages/Home";
import Login     from "../pages/Login";
import Register  from "../pages/Register";
import Dashboard from "../pages/Dashboard";
import Galeria   from "../pages/Galeria";

export default function AppRoutes() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Rutas públicas */}
          <Route path="/"         element={<Welcome />} />
          <Route path="/home"     element={<Home />} />
          <Route path="/login"    element={<Login />} />
          <Route path="/registro" element={<Register />} />

          {/* Rutas protegidas — redirigen a /login si no hay sesión */}
          <Route path="/dashboard" element={
            <PrivateRoute><Dashboard /></PrivateRoute>
          } />
          <Route path="/galeria" element={
            <PrivateRoute><Galeria /></PrivateRoute>
          } />

          {/* Cualquier ruta desconocida redirige a home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
