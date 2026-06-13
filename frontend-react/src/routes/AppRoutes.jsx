import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider } from "../context/AuthContext";
import PrivateRoute    from "./PrivateRoute";
import Upload from "../pages/Upload";
import Welcome        from "../pages/Welcome";
import Home           from "../pages/Home";
import Login          from "../pages/Login";
import Register       from "../pages/Register";
import Dashboard      from "../pages/Dashboard";
import Galeria        from "../pages/Galeria";
import AdminLogin     from "../pages/AdminLogin";
import AdminDashboard from "../pages/AdminDashboard";
import ChatPersona    from "../pages/ChatPersona";

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
          <Route path="/upload" element={
            <PrivateRoute><Upload /></PrivateRoute>
} />
          <Route path="/chat/:nombre" element={
            <PrivateRoute><ChatPersona /></PrivateRoute>
          } />

          {/* Admin */}
          <Route path="/admin" element={<AdminLogin />} />
          <Route path="/admin/dashboard" element={
            <PrivateRoute><AdminDashboard /></PrivateRoute>
          } />

          {/* Cualquier ruta desconocida redirige a home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
