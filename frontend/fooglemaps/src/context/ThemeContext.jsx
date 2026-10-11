import { createContext, useContext, useState, useEffect, useCallback } from "react";

const STORAGE_KEY = "fooglemaps-theme";

function getStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY) || "light";
  } catch {
    return "light";
  }
}

function getSystemTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function resolveTheme(preference) {
  return preference === "system" ? getSystemTheme() : preference;
}

function applyTheme(resolved) {
  document.documentElement.setAttribute("data-theme", resolved);
}

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [preference, setPreference] = useState(getStoredTheme);

  const resolved = resolveTheme(preference);

  useEffect(() => {
    applyTheme(resolved);
    try {
      localStorage.setItem(STORAGE_KEY, preference);
    } catch {}
  }, [preference, resolved]);

  useEffect(() => {
    if (preference !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => applyTheme(resolveTheme("system"));
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [preference]);

  const setTheme = useCallback((p) => setPreference(p), []);

  return (
    <ThemeContext.Provider value={{ preference, resolved, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}
