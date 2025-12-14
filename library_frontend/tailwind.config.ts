import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}', // Include constants with dynamic classes
  ],
  safelist: [
    // Loyalty badge colors (dynamic classes from LOYALTY_BADGES)
    'bg-gray-100', 'text-gray-600',
    'bg-gradient-to-r', 'from-gray-200', 'to-gray-300', 'text-gray-700',
    'from-amber-100', 'to-amber-200', 'text-amber-700',
    'from-purple-100', 'to-purple-200', 'text-purple-700',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#EC4899',
          50: '#FDF2F8',
          100: '#FCE7F3',
          200: '#FBCFE8',
          300: '#F9A8D4',
          400: '#F472B6',
          500: '#EC4899',
          600: '#DB2777',
          700: '#BE185D',
          800: '#9D174D',
          900: '#831843',
        },
        accent: '#FDE68A',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
      },
    },
  },
  plugins: [],
}

export default config
