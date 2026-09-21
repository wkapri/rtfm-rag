import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // bind 0.0.0.0 so other devices on the LAN can reach the dev server
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000", // Vite process itself runs on this machine, so localhost is correct here
    },
  },
});
