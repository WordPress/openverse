/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
  testDir: 'test/e2e',
  use: {
    baseURL: 'http://localhost:8443',
  },
  timeout: 1 * 60 * 1000,
}
module.exports = config
