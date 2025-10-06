/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Use class-based dark mode
  safelist: [
    // Force include dark mode classes
    'dark:bg-gray-900',
    'dark:bg-gray-800', 
    'dark:bg-gray-700',
    'dark:text-gray-100',
    'dark:text-gray-300',
    'dark:text-gray-400',
    'dark:text-gray-500',
    'dark:text-primary-400',
    'dark:text-primary-300',
    'dark:border-gray-700',
    'dark:border-gray-600',
    'dark:border-gray-500',
    'dark:hover:bg-gray-700',
    'dark:hover:bg-gray-600',
    'dark:hover:text-gray-300',
    'dark:hover:text-primary-300',
    'dark:hover:border-primary-400',
    'dark:bg-primary-900/50',
    'dark:bg-primary-900/20',
    'dark:bg-red-900/20',
    'dark:border-red-500',
    'dark:text-red-400',
    'dark:shadow-gray-900/20',
    'dark:placeholder-gray-400'
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
