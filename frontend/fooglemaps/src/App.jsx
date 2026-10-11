import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { SidebarProvider } from "./context/SidebarContext";
import { ThemeProvider } from "./context/ThemeContext";
import { AuthProvider } from "./context/AuthContext";
import { CuisineProvider } from "./context/CuisineContext";
import MainLayout from "./components/MainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import HomePage from "./pages/HomePage";
import MapsPage from "./pages/MapsPage";
import FeedPage from "./pages/FeedPage";
import SearchPage from "./pages/SearchPage";
import SavedPage from "./pages/SavedPage";
import SettingsPage from "./pages/SettingsPage";
import SignInPage from "./pages/SignInPage";

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <SidebarProvider>
          <AuthProvider>
            <CuisineProvider>
              <Routes>
                <Route path="/signin" element={<SignInPage />} />
                <Route element={<MainLayout />}>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/maps" element={<MapsPage />} />
                  <Route path="/feed" element={<FeedPage />} />
                  <Route path="/search" element={<SearchPage />} />
                  <Route path="/saved" element={<ProtectedRoute><SavedPage /></ProtectedRoute>} />
                  <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Route>
              </Routes>
            </CuisineProvider>
          </AuthProvider>
        </SidebarProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
