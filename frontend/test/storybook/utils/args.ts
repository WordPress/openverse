import type { LanguageDirection } from "~~/test/playwright/utils/i18n"

import type { Page } from "@playwright/test"

export const dirParam = (dir: LanguageDirection) => {
  return dir === "ltr" ? "" : "&globals=languageDirection:rtl"
}

const buildUrl = (
  storySlug: string,
  args?: Record<string, unknown>,
  dir: LanguageDirection = "ltr"
) => {
  const argStrings = Object.entries(args ?? {})
    .map(([k, v]) => `${k}:${v}`)
    .join(";")
  const argsParam = args ? `&args=${argStrings}` : ""
  return `/iframe.html?id=${storySlug}${argsParam}${dirParam(dir)}`
}

export const makeUrlWithArgs =
  (storySlug: string) =>
  (args?: Record<string, unknown>, dir: LanguageDirection = "ltr") => {
    return buildUrl(storySlug, args, dir)
  }

export const makeGotoWithArgs =
  (storySlug: string) =>
  (
    page: Page,
    args?: Record<string, unknown>,
    dir: LanguageDirection = "ltr"
  ) => {
    const url = buildUrl(storySlug, args, dir)
    return page.goto(url)
  }
