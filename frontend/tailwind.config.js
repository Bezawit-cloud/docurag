/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        paper: '#FAFAF8',
        ink: '#1B2733',
        slate: '#6B7280',
        teal: {
          DEFAULT: '#1F4B4F',
          dark: '#163638',
        },
        highlighter: '#F4C94B',
        clay: '#C97D52',
        line: '#E4E0D8',
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        tab: '3px 10px 10px 3px',
      },
    },
  },
  plugins: [],
};
