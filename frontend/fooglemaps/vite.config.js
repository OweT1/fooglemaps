import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
    headers: {
      "Cross-Origin-Opener-Policy": "unsafe-none",
    },
  },
  envPrefix: ["GOOGLE_"],
});
