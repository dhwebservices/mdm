import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        surface: "#f7f8fb",
        line: "#d7dce5",
        brand: "#0f766e"
      }
    }
  },
  plugins: []
} satisfies Config;
