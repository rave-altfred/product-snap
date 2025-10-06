/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Use class-based dark mode
  safelist: [
    {
      pattern: /^(bg|text|border|hover:bg|hover:text|hover:border|placeholder)-(gray|primary|red)-(50|100|200|300|400|500|600|700|800|900)$/,
      variants: ['dark', 'hover', 'dark:hover'],
    },
    {
      pattern: /^dark:(bg|text|border|hover:bg|hover:text|hover:border|shadow|placeholder)/,
    },
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        },
      },
    },
  },
  plugins: [],
}
