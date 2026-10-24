/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Core Palette extracted from inspiration image:
        // #071739 - Deep Midnight Navy
        // #4B6382 - Steel Slate Blue
        // #A4B5C4 - Soft Mist Blue
        // #CDD5DB - Pale Slate / Ice Gray
        // #A68868 - Warm Sandstone / Muted Camel
        // #E3C39D - Soft Oat / Creamy Warm Sand
        palette: {
          navy: '#071739',
          slate: '#4B6382',
          mist: '#A4B5C4',
          pale: '#CDD5DB',
          clay: '#A68868',
          sand: '#E3C39D',
          cream: '#F7F5EE',
          surface: '#FFFFFF',
          border: '#E5DFD5',
        },
        dark: {
          bg: '#071739',          // Deep Midnight Navy in dark mode
          surface: '#0E244B',     // Elevated navy surface
          card: '#122D5C',        // Elevated navy card
          hover: '#193B74',       // Interactive hover
          border: '#244983',      // Boundary
          muted: '#A4B5C4',
        },
        accent: {
          DEFAULT: '#071739',     // Primary action: Deep Midnight Navy
          hover: '#4B6382',       // Hover: Slate Blue
          light: '#4B6382',
          glow: 'rgba(7, 23, 57, 0.15)',
          navy: '#071739',
          slate: '#4B6382',
          mist: '#A4B5C4',
          pale: '#CDD5DB',
          clay: '#A68868',
          sand: '#E3C39D',
          teal: '#3B737A',
          emerald: '#2C7A5C',
          amber: '#A68868',
          rose: '#A65555',
        },
        app: {
          text: '#071739',        // Primary text: Deep Navy
          muted: '#4B6382',       // Secondary text: Slate Blue
          subtle: '#728599',      // Tertiary text: Soft Slate
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'soft-card': '0 8px 30px -4px rgba(7, 23, 57, 0.05), 0 2px 8px -2px rgba(7, 23, 57, 0.03)',
        'soft-card-hover': '0 12px 35px -4px rgba(7, 23, 57, 0.09), 0 4px 12px -2px rgba(7, 23, 57, 0.05)',
        'glow-navy': '0 4px 20px rgba(7, 23, 57, 0.20)',
        'glow-sand': '0 4px 20px rgba(166, 136, 104, 0.25)',
        'glow-sm': '0 2px 10px rgba(7, 23, 57, 0.12)',
        'glow-md': '0 4px 20px rgba(7, 23, 57, 0.18)',
        'card-dark': '0 6px 24px rgba(0, 0, 0, 0.25)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'wave': 'wave 1.2s ease-in-out infinite alternate',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        wave: {
          '0%': { height: '15%' },
          '100%': { height: '100%' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        }
      }
    },
  },
  plugins: [],
}
