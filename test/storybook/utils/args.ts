import type { Page } from '@playwright/test'

export const makeGotoWithArgs =
  (storySlug: string) => (page: Page, args?: Record<string, unknown>) => {
    const argStrings = Object.entries(args ?? {})
      .map(([k, v]) => `${k}:${v}`)
      .join(';')
    const argsParam = args ? `&args=${argStrings}` : ''

    const url = `/iframe.html?id=${storySlug}${argsParam}`
    return page.goto(url)
  }
