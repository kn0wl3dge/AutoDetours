module.exports = {
  root: true,
  env: {
    browser: true,
    node: true
  },
  parserOptions: {
    parser: 'babel-eslint',
    sourceType: 'module'
  },
  extends: [
    '@nuxtjs',
    'plugin:nuxt/recommended',
    'plugin:eslint-plugin-nuxt'
  ],
  plugins: [],
  // add your custom rules here
  rules: {}
}