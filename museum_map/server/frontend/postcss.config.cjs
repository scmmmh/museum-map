import tailwindcss from 'tailwindcss'
import tailwindcssConfig from './tailwind.config.cjs'
import autoprefixer from 'autoprefixer'

module.exports = {
  plugins: [
    tailwindcss(tailwindcssConfig),
    autoprefixer,
  ]
}
