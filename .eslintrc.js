module.exports = {
  root: true,
  extends: ["plugin:@openverse/project"],
  plugins: ["@openverse"],
  rules: {
    // Add or override rules here
    curly: ['error', 'all'],
    'default-case': 'error',
    eqeqeq: 'error',
  },
};
