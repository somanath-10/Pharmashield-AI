import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        sand: "#f6efe3",
        mint: "#c8f2d4",
        coral: "#f58f74",
        slateblue: "#3b4b74",
        cloud: "#f8fafc"
      },
      boxShadow: {
        panel: "0 24px 60px rgba(17, 24, 39, 0.14)"
      },
      borderRadius: {
        xl2: "1.5rem"
      }
    }
  },
  plugins: []
};

export default config;
