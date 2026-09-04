import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider } from "../context/AuthContext";
import PrivateRoute from "./PrivateRoute";
import Upload from "../pages/Upload";
import Welcome from "../pages/Welcome";
import Home from "../pages/Home";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard";
import Galeria from "../pages/Galeria";
import AdminLogin from "../pages/AdminLogin";
import AdminDashboard from "../pages/AdminDashboard";
import PersonaChat from "../pages/PersonaChat";

export default function AppRoutes() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Welcome />} />
          <Route path="/home" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Register />} />

          <Route path="/p/:personaId" element={<PersonaChat />} />

          <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/galeria" element={<PrivateRoute><Galeria /></PrivateRoute>} />
          <Route path="/upload" element={<PrivateRoute><Upload /></PrivateRoute>} />

          <Route path="/admin" element={<AdminLogin />} />
          <Route path="/admin/dashboard" element={<PrivateRoute><AdminDashboard /></PrivateRoute>} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
