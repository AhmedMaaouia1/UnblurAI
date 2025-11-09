/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#60A5FA',
        dark: '#1E293B',
        light: '#F9FAFB',
      },
    },
  },
  plugins: [],
}
