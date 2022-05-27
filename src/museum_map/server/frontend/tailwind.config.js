module.exports = {
  content: [
    './src/**/*.svelte',
  ],
  theme: {
    extend: {
      boxShadow: {
        even: '0 0 10px var(--tw-shadow-color)',
        'even-lg': '0 0 20px var(--tw-shadow-color)',
      }
    },
  },
  plugins: [],
}
