/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.svelte',
  ],
  theme: {
    extend: {
      boxShadow: {
        even: '0 0 10px var(--tw-shadow-color)',
        'even-lg': '0 0 20px var(--tw-shadow-color)',
      },
      letterSpacing: {
        default: '0.04em',
      },
      gridTemplateColumns: {
        'items': 'repeat(auto-fill, 240px);',
      },
      maxHeight: {
        '1/2': '50%',
        '4/6': '66.666666%',
        '5/6': '83.333333%'
      }
    },
  },
  plugins: [],
}
