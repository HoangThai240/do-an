/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2563eb",
        primaryHover: "#1d4ed8",
        secondary: "#64748b",
        accent: "#f59e0b",
        lightBg: "#f8fafc",
        darkBg: "#0f172a",
      },
    },
  },
  plugins: [],
}