import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { SidebarProvider } from "./context/SidebarContext";
import { ThemeProvider } from "./context/ThemeContext";
import MainLayout from "./components/MainLayout";
import HomePage from "./pages/HomePage";
import MapsPage from "./pages/MapsPage";
import SearchPage from "./pages/SearchPage";
import SavedPage from "./pages/SavedPage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <SidebarProvider>
          <MainLayout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/maps" element={<MapsPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/saved" element={<SavedPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </MainLayout>
        </SidebarProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
