/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './public/index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {},
  },
  safelist: [
    { pattern: /bg-(blue|green|purple|orange|yellow|red)-(100|400|500|600)/ },
    { pattern: /text-(blue|green|purple|orange|yellow|red)-(400|500|600|700|800)/ },
  ],
  plugins: [
    require('@tailwindcss/line-clamp'),
  ],
};
