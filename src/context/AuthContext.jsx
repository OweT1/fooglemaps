import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { useNavigate } from "react-router-dom";
import { useTheme } from "./ThemeContext";
import config from "../config/config";

const STORAGE_KEY = "fooglemaps-auth";

function decodeJwt(token) {
  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch {
    return null;
  }
}

function loadSession() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveSession(data) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {}
}

function clearSession() {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {}
}

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { setTheme } = useTheme();

  useEffect(() => {
    const saved = loadSession();
    if (saved?.credential) {
      fetch("/api/auth/me", {
        headers: { Authorization: `Bearer ${saved.credential}` },
      })
        .then((res) => {
          if (!res.ok) throw new Error("Session expired");
          return res.json();
        })
        .then((data) => {
          setUser(data.user);
          setSettings(data.settings);
          if (data.settings?.theme) setTheme(data.settings.theme);
        })
        .catch(() => {
          clearSession();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // const redirectToSignIn = navigate("/signin");

  const signIn = useCallback(() => {
    if (!window.google?.accounts?.oauth2) {
      console.error("Google Identity Services not loaded yet");
      alert(
        "Google Sign-In is still loading. Please wait a moment and try again.",
      );
      return;
    }
    try {
      const client = google.accounts.oauth2.initTokenClient({
        client_id: config.GOOGLE_OAUTH.CLIENT_ID,
        scope: "openid email profile",
        callback: (response) => {
          if (response.error) {
            console.error("Google OAuth error:", response.error);
            return;
          }
          const user_token = response.access_token;

          fetch("/api/auth/login", {
            method: "POST",
            headers: { Authorization: `Bearer ${user_token}` },
          })
            .then((res) => {
              if (!res.ok) throw new Error("Login failed");
              return res.json();
            })
            .then((data) => {
              const session = {
                user: data.user,
                settings: data.settings,
                credential: user_token,
              };
              setUser(data.user);
              setSettings(data.settings);
              if (data.settings?.theme) setTheme(data.settings.theme);
              saveSession(session);
              navigate("/", { replace: true });
            })
            .catch((err) => {
              console.error("Sign-in error:", err);
            });
        },
      });
      client.requestAccessToken();
    } catch (err) {
      console.error("GIS initTokenClient error:", err);
    }
  }, [navigate, setTheme]);

  const updateSettings = useCallback(
    async (updates) => {
      const saved = loadSession();
      if (!saved?.credential) return;

      const res = await fetch("/api/settings", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${saved.credential}`,
        },
        body: JSON.stringify(updates),
      });
      if (!res.ok) return;

      const data = await res.json();
      setSettings(data.settings);
      if (data.settings?.theme) setTheme(data.settings.theme);

      const updated = { ...saved, settings: data.settings };
      saveSession(updated);
    },
    [setTheme],
  );

  const signOut = useCallback(() => {
    if (window.google?.accounts) {
      google.accounts.id.disableAutoSelect();
    }
    setUser(null);
    setSettings(null);
    clearSession();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        settings,
        loading,
        // redirectToSignIn,
        signIn,
        signOut,
        updateSettings,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
