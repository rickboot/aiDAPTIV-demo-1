/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // "Shreyu" Admin Theme Colors
        dashboard: {
          bg: '#313a46',      // Main Page Background (Dark Blue-Gray)
          card: '#37404a',    // Element Background
          border: '#434e5b',  // Subtle Border
        },
        text: {
          primary: '#f3f4f6',   // White-ish
          secondary: '#98a6ad', // The distinct muted blue-gray text from the image
          muted: '#6c757d',
        },
        accent: {
          primary: '#5369f8',   // Vibrant Blue
          success: '#0acf97',   // Vibrant Green
          danger: '#fa5c7c',    // Salmon Red
          warning: '#ffbc00',   // Amber
          info: '#39afd1',      // Cyan
        }
      },
      fontFamily: {
        sans: ['"Inter"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 0.75rem 1.5rem rgba(18, 38, 63, 0.03)',
      }
    },
  },
  plugins: [],
}
