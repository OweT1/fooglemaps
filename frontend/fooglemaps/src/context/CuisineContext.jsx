import { createContext, useCallback, useContext, useEffect, useState } from "react";

const CuisineContext = createContext();

export function CuisineProvider({ children }) {
  const [cuisines, setCuisines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    fetch("/api/cuisines")
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => {
        if (!active) return;
        setCuisines(
          Array.isArray(data)
            ? data.map((c) => (typeof c === "string" ? c : c.name)).filter(Boolean)
            : []
        );
      })
      .catch(() => {})
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const has = useCallback((name) => cuisines.includes(name), [cuisines]);

  return (
    <CuisineContext.Provider value={{ cuisines, loading, has }}>
      {children}
    </CuisineContext.Provider>
  );
}

export function useCuisines() {
  const ctx = useContext(CuisineContext);
  if (!ctx) throw new Error("useCuisines must be used within CuisineProvider");
  return ctx;
}
