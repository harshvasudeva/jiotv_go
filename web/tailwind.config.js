/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./views/*.html", "./static/internal/*.js"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "SF Pro Display",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "system-ui",
          "sans-serif",
        ],
      },
      boxShadow: {
        // Layered elevation: a single soft shadow disappears on dark canvases,
        // so each level pairs a tight contact shadow with a wide ambient one.
        elevated: "0 1px 2px rgb(0 0 0 / 0.28), 0 12px 32px -8px rgb(0 0 0 / 0.5)",
        float: "0 2px 6px rgb(0 0 0 / 0.3), 0 24px 56px -12px rgb(0 0 0 / 0.62)",
      },
      transitionTimingFunction: {
        "out-expo": "cubic-bezier(0.16, 1, 0.3, 1)",
      },
      keyframes: {
        "fade-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) both",
      },
    },
  },
  plugins: [require("daisyui"), require("@tailwindcss/line-clamp")],
  daisyui: {
    themes: [
      {
        // Cinematic dark theme: near-black canvas with layered surfaces and a
        // single saturated accent, so artwork stays the loudest thing on screen.
        dark: {
          primary: "#e11d48",
          "primary-content": "#ffffff",
          secondary: "#8b5cf6",
          "secondary-content": "#ffffff",
          accent: "#f43f5e",
          "accent-content": "#ffffff",
          neutral: "#161821",
          "neutral-content": "#e7e9ee",
          "base-100": "#0f1117",
          "base-200": "#080910",
          "base-300": "#232735",
          "base-content": "#e9ebf0",
          info: "#38bdf8",
          success: "#22c55e",
          warning: "#f59e0b",
          error: "#ef4444",
          "--rounded-box": "1.15rem",
          "--rounded-btn": "0.7rem",
          "--animation-btn": "0.2s",
        },
      },
      {
        light: {
          primary: "#e11d48",
          "primary-content": "#ffffff",
          secondary: "#7c3aed",
          "secondary-content": "#ffffff",
          accent: "#f43f5e",
          "accent-content": "#ffffff",
          neutral: "#1f2430",
          "neutral-content": "#f6f7f9",
          "base-100": "#ffffff",
          "base-200": "#f4f5f8",
          "base-300": "#e3e6ec",
          "base-content": "#14161c",
          info: "#0284c7",
          success: "#16a34a",
          warning: "#d97706",
          error: "#dc2626",
          "--rounded-box": "1.15rem",
          "--rounded-btn": "0.7rem",
          "--animation-btn": "0.2s",
        },
      },
    ],
    darkTheme: "dark",
  },
};
