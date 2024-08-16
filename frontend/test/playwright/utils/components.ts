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

export const getMenuButton = (page: Page, dir: LanguageDirection = "ltr") =>
  page.getByRole("button", { name: t("header.aria.menu", dir) })

export const getBackToSearchLink = (
  page: Page,
  dir: LanguageDirection = "ltr",
  locale: "es" | "ru" | undefined = undefined
) => {
  return page.getByRole("link", { name: t("singleResult.back", dir, locale) })
}

export const skipToContentLink = (page: Page, dir: LanguageDirection = "ltr") =>
  page.getByRole("link", { name: t("skipToContent", dir) })

export const getHomeLink = (page: Page, dir: LanguageDirection = "ltr") =>
  page
    .getByRole("banner")
    .getByRole("link", { name: t("header.homeLink", dir) })

export const getHomepageSearchButton = (
  page: Page,
  dir: LanguageDirection = "ltr"
) => page.getByRole("button", { name: t("search.search", dir) })

export const getLanguageSelect = (page: Page, dir: LanguageDirection = "ltr") =>
  page.getByRole("combobox", { name: t("language.language", dir) })

export const getHeaderSearchbar = (
  page: Page,
  dir: LanguageDirection = "ltr"
) => page.getByRole("combobox", { name: t("search.searchBarLabel", dir) })
