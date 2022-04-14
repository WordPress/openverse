import path from 'path'

import { addAliases } from 'module-alias'

import type { PlaywrightTestConfig } from '@playwright/test'

addAliases({
  '~': path.resolve(process.cwd(), 'src'),
  '~~': process.cwd(),
})

const config: PlaywrightTestConfig = {
  webServer: {
    command: 'pnpm storybook',
    timeout: 60_000 * 5, // 5 minutes
    port: 54000,
    reuseExistingServer: !process.env.CI || process.env.PWDEBUG === '1',
  },
  use: {
    baseURL: 'http://localhost:54000',
    trace: 'retain-on-failure',
  },
  timeout: 2 * 60 * 1e3,
}

export default config
