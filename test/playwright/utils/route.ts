import type { BrowserContext } from '@playwright/test'

export const mockProviderApis = async (context: BrowserContext) => {
  await context.route('**.jamendo.com**', (route) => route.abort())
  await context.route('**.freesound.**', (r) => r.abort())
}
