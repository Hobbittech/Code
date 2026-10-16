import { Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/Landing";
import Workstation from "./pages/Workstation";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/workstation" element={<Workstation />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
