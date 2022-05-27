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
    },
  },
  plugins: [],
}
