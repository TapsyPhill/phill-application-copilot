import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export default defineConfig({
  plugins: [react()],
  // Load .env from repo root (where SUPABASE / VITE_* keys live)
  envDir: rootDir,
  server: { port: 5173 },
});
