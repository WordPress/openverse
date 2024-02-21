import { Page } from "@playwright/test"

import { LanguageDirection, t } from "~~/test/playwright/utils/i18n"

export const getCopyButton = (page: Page, dir: LanguageDirection = "ltr") =>
  page.getByRole("button", {
    name: t("mediaDetails.reuse.copyLicense.copyText", dir),
  })

export const getLoadMoreButton = (page: Page, dir: LanguageDirection = "ltr") =>
  page.getByRole("button", {
    name: t("browsePage.load", dir),
  })

export const getH1 = (page: Page, text: string | RegExp) =>
  page.getByRole("heading", { level: 1, name: text })

export const getMenuButton = async (page: Page) => {
  return page.locator("#menu-button")
}

export const getBackToSearchLink = (
  page: Page,
  dir: LanguageDirection = "ltr",
  locale: "es" | "ru" | undefined = undefined
) => {
  return page.getByRole("link", { name: t("singleResult.back", dir, locale) })
}

// Get the header home link. Hard-codes the text because `t` does not support interpolation.
export const getHomeLink = (page: Page) =>
  page.getByRole("banner").getByRole("link", { name: "Openverse Home" })
