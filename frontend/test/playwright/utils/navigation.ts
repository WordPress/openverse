import { expect } from "@playwright/test"

import rtlMessages from "~~/test/locales/ar.json"

import enMessages from "~/locales/en.json"

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  MediaType,
  MODEL_3D,
  searchPath,
  SupportedSearchType,
  VIDEO,
} from "~/constants/media"

import type { Breakpoint } from "~/constants/screens"

import type { BrowserContext, Locator, Page } from "@playwright/test"

const messages: Record<string, Record<string, unknown>> = {
  ltr: enMessages,
  rtl: rtlMessages,
}

const getNestedProperty = (
  obj: Record<string, unknown>,
  path: string
): string => {
  const value = path
    .split(".")
    .reduce((acc: string | Record<string, unknown>, part) => {
      if (typeof acc === "string") {
        return acc
      }
      if (Object.keys(acc as Record<string, unknown>).includes(part)) {
        return (acc as Record<string, string | Record<string, unknown>>)[part]
      }
      return ""
    }, obj)
  return typeof value === "string" ? value : JSON.stringify(value)
}

/**
 * Simplified i18n t function that returns English messages for `ltr` and Arabic for `rtl`.
 * It can handle nested labels that use the dot notation ('header.title').
 * @param path - The label to translate.
 * @param dir - The language direction.
 */
export const t = (path: string, dir: LanguageDirection = "ltr"): string => {
  let value = ""
  if (dir === "rtl") {
    value = getNestedProperty(messages.rtl, path)
  }
  return value === "" ? getNestedProperty(messages.ltr, path) : value
}

export const languageDirections = ["ltr", "rtl"] as const

export const renderingContexts = [
  ["SSR", "ltr"],
  ["SSR", "rtl"],
  ["CSR", "ltr"],
  ["CSR", "rtl"],
] as const

export const renderModes = ["SSR", "CSR"] as const
export type RenderMode = (typeof renderModes)[number]
export type LanguageDirection = (typeof languageDirections)[number]

export function sleep(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms))
}

export type CheckboxStatus = "checked" | "unchecked" | "disabled"

export const searchTypeNames = {
  ltr: {
    [ALL_MEDIA]: t("searchType.all", "ltr"),
    [AUDIO]: t("searchType.audio", "ltr"),
    [IMAGE]: t("searchType.image", "ltr"),
    [VIDEO]: t("searchType.video", "ltr"),
    [MODEL_3D]: t("searchType.model-3d", "ltr"),
  },
  rtl: {
    [ALL_MEDIA]: t("searchType.all", "rtl"),
    [AUDIO]: t("searchType.audio", "rtl"),
    [IMAGE]: t("searchType.image", "rtl"),
    [VIDEO]: t("searchType.video", "rtl"),
    [MODEL_3D]: t("searchType.model3d", "rtl"),
  },
}

/**
 * On mobile screen, open the "tab" in the content settings modal.
 * Should be called after the modal is open.
 */
export const openContentSettingsTab = async (
  page: Page,
  tab: "searchTypes" | "filters" = "searchTypes",
  dir: LanguageDirection = "ltr"
) => {
  const tabKey = tab === "searchTypes" ? "searchType.heading" : "filters.title"

  await page.getByRole("tab", { name: t(tabKey, dir) }).click()
}

/**
 * On mobile screen, clicks on the "Close" button in the content settings modal.
 */
export const closeContentSettingsModal = async (
  page: Page,
  dir: LanguageDirection = "ltr"
) => {
  return page
    .getByRole("button", { name: t("modal.closeContentSettings", dir) })
    .click()
}

/**
 * Opens or closes the search settings:
 * - given modal tab on mobile screen
 * - filters sidebar or the search types popover on desktop screen
 */
export const setContentSwitcherState = async (
  page: Page,
  contentSwitcherKind: "filters" | "searchTypes",
  state: "open" | "closed",
  dir: LanguageDirection = "ltr"
) => {
  const isDesktop = isPageDesktop(page)

  const buttonLocator = page.locator(
    !isDesktop
      ? "#content-settings-button"
      : contentSwitcherKind === "filters"
      ? "#filter-button"
      : "#search-type-button"
  )

  const isPressed = await getSelectorPressed(buttonLocator)
  const shouldBePressed = state === "open"

  if (isDesktop) {
    if (isPressed === shouldBePressed) {
      return null
    }
    return await buttonLocator.click()
  }

  if (shouldBePressed) {
    if (!isPressed) {
      await buttonLocator.click()
    }
    return openContentSettingsTab(page, contentSwitcherKind, dir)
  } else if (isPressed) {
    await closeContentSettingsModal(page, dir)
  }
}

export const filters = {
  open: async (page: Page, dir: LanguageDirection = "ltr") => {
    await setContentSwitcherState(page, "filters", "open", dir)
  },
  close: async (page: Page, dir: LanguageDirection = "ltr") => {
    await setContentSwitcherState(page, "filters", "closed", dir)
  },
}

export const searchTypes = {
  open: async (page: Page, dir: LanguageDirection = "ltr") => {
    await setContentSwitcherState(page, "searchTypes", "open", dir)
  },
  close: async (page: Page, dir: LanguageDirection = "ltr") => {
    await setContentSwitcherState(page, "searchTypes", "closed", dir)
  },
}

export const isPageDesktop = (page: Page) => {
  const pageWidth = page.viewportSize()?.width
  if (!pageWidth) {
    return false
  }
  const desktopMinWidth = 1024
  return pageWidth >= desktopMinWidth
}

/**
 * Returns true if the button with the given selector is pressed or expanded.
 */
const getSelectorPressed = async (selector: Locator) => {
  return (
    (await selector.getAttribute("aria-pressed")) === "true" ||
    (await selector.getAttribute("aria-expanded")) === "true"
  )
}

export const isDialogOpen = async (page: Page) => {
  return page.getByRole("dialog").isVisible({ timeout: 100 })
}

export const changeSearchType = async (page: Page, to: SupportedSearchType) => {
  await searchTypes.open(page)

  const changedUrl = new RegExp(to === ALL_MEDIA ? `/search?` : `/search/${to}`)
  await page.getByRole("radio", { name: searchTypeNames.ltr[to] }).click()
  await page.waitForURL(changedUrl)

  await searchTypes.close(page)
}

/**
 * Returns the name of the currently selected search type.
 * Opens the content switcher and selects the text content of the checked
 * radio item.
 */
export const currentContentType = async (page: Page) => {
  await searchTypes.open(page)
  const currentContentType =
    (await page.getByRole("radio", { checked: true }).textContent())?.trim() ??
    ""
  await searchTypes.close(page)

  return currentContentType
}

export const selectHomepageSearchType = async (
  page: Page,
  searchType: SupportedSearchType,
  dir: LanguageDirection = "ltr"
) => {
  await page
    .getByRole("button", { name: searchTypeNames[dir][ALL_MEDIA] })
    .click()
  await page
    .getByRole("radio", { name: searchTypeNames[dir][searchType] })
    .click()
}

const ALL_TEST_BANNERS = [
  ...["ru", "en", "ar", "es"].map((lang) => `translation-${lang}`),
  "analytics",
]
export const preparePageForTests = async (
  page: Page,
  breakpoint: Breakpoint,
  options: Partial<{
    features: Record<string, "on" | "off">
    dismissBanners: boolean
    dismissFilter: boolean
  }> = {}
) => {
  const { features = {}, dismissBanners = true, dismissFilter = true } = options
  const featuresCookie: Record<string, "on" | "off"> = {}
  if (options.features) {
    for (const [feature, status] of Object.entries(features)) {
      featuresCookie[feature] = status
    }
  }
  await setCookies(page.context(), {
    features: featuresCookie,
    ui: {
      dismissedBanners: dismissBanners ? ALL_TEST_BANNERS : [],
      isFilterDismissed: dismissFilter ?? false,
      breakpoint,
    },
  })
}

export const goToSearchTerm = async (
  page: Page,
  term: string,
  options: {
    searchType?: SupportedSearchType
    mode?: RenderMode
    dir?: LanguageDirection
    query?: string // Only for SSR mode
  } = {}
) => {
  const searchType = options.searchType || ALL_MEDIA
  const dir = options.dir || "ltr"
  const mode = options.mode ?? "SSR"
  const query = options.query ? `&${options.query}` : ""

  if (mode === "SSR") {
    const path = `${searchPath(searchType)}?q=${term}${query}`
    await page.goto(pathWithDir(path, dir))
  } else {
    await page.goto(pathWithDir("/", dir))
    // Select the search type
    if (searchType !== "all") {
      await selectHomepageSearchType(page, searchType, dir)
    }
    // Type search term
    const searchInput = page.locator('main input[type="search"]')
    await searchInput.type(term)
    // Click search button
    // Wait for navigation
    await page.getByRole("button", { name: t("search.search", dir) }).click()
    await page.waitForURL(/search/, { waitUntil: "load" })
  }
  await scrollDownAndUp(page)
}

/**
 * Fills the search input in the page header, clicks on submit
 * and waits for navigation.
 */
export const searchFromHeader = async (page: Page, term: string) => {
  // Double-click on the search bar to remove previous value
  await page.dblclick("id=search-bar")
  await page.fill("id=search-bar", term)
  await page.keyboard.press("Enter")
  await page.waitForURL(/search/)
}

/**
 * Click on the first <mediaType> result: a link that contains
 * /<mediaType>/ in its URL. We cannot use the 'startsWith' `^` matcher
 * because localized routes start with the locale prefix (e.g. /ar/image/).
 * Scroll down and up to load all lazy-loaded content.
 */
export const openFirstResult = async (page: Page, mediaType: MediaType) => {
  const firstResult = page.locator(`a[href*="/${mediaType}/"]`).first()
  const firstResultHref = await getLocatorHref(firstResult)
  await firstResult.click({ position: { x: 32, y: 32 } })

  // Make sure that navigation to single result page is complete.
  // Using URL is not enough because it changes before navigation is complete.
  await expect(page.getByRole("heading", { name: /how to use/i })).toBeVisible()

  await scrollDownAndUp(page)
  // Wait for all pending requests to finish, at which point we know
  // that all lazy-loaded content is available
  // eslint-disable-next-line playwright/no-networkidle
  await page.waitForURL(firstResultHref, { waitUntil: "networkidle" })
  await page.mouse.move(0, 0)
}

export const getLocatorHref = async (locator: Locator) => {
  const href = await locator.getAttribute("href")
  if (!href) {
    throw new Error("Could not find href attribute")
  }
  return href
}

/**
 * Scroll the site to the "end" (top or bottom) of the primary scrollable element, either:
 * - the `window`, on interior pages
 * - the `#main-page`, on search views
 *
 * This is necessary because on search views the window itself does not scroll, only
 * its child elements (the search result area + the filter sidebar).
 *
 * This function will scroll both elements on every evocation.
 */
export const fullScroll = async (
  page: Page,
  direction: "bottom" | "top" = "bottom"
) => {
  await page.evaluate((direction) => {
    const mainPage = document.getElementById("main-page")
    mainPage?.scrollTo(0, direction === "top" ? 0 : mainPage?.scrollHeight)
    window.scrollTo(0, direction === "top" ? 0 : document.body.scrollHeight)
  }, direction)
}

export const scrollToTop = async (page: Page) => {
  await fullScroll(page, "top")
  await sleep(200) // TODO: Is this necessary?
}

export const scrollToBottom = async (page: Page) => {
  await fullScroll(page, "bottom")
  await sleep(200) // TODO: Is this necessary?
}

/**
 * Used to load all lazy-loaded images in the page.
 */
export const scrollDownAndUp = async (page: Page) => {
  await scrollToBottom(page)
  await page.waitForLoadState("load")
  await scrollToTop(page)
}

/**
 * Adds '/ar' prefix to a rtl route. The path should start with '/'
 */
export const pathWithDir = (rawPath: string, dir: string) => {
  const path = rawPath.startsWith("/") ? rawPath : `/${rawPath}`
  return dir === "rtl" ? `/ar${path}` : path
}

export interface CookieMap {
  [key: string]: string | boolean | string[] | CookieMap
}

export const setCookies = async (
  context: BrowserContext,
  cookies: CookieMap
) => {
  const existingCookies = await context.cookies()
  const cookiesToSet = Object.entries(cookies).map(([name, value]) => {
    let existingValue = existingCookies.find((c) => c.name === name)?.value

    // If cookie was URI encoded, it starts with %7B%22 `{"` or %5B%22 `["`
    if (
      existingValue &&
      (existingValue.includes("%7B%22") || existingValue.includes("%5B%22"))
    ) {
      existingValue = decodeURIComponent(existingValue)
    }
    let newCookieValue = ""
    if (existingValue) {
      if (Array.isArray(value)) {
        newCookieValue = JSON.stringify(
          Array.from(new Set([...JSON.parse(existingValue), ...value]))
        )
      } else if (typeof value === "string") {
        newCookieValue = value
      } else if (typeof value === "object") {
        newCookieValue = JSON.stringify({
          ...JSON.parse(existingValue),
          ...value,
        })
      } else if (typeof value === "boolean") {
        newCookieValue = String(value)
      }
    } else {
      newCookieValue = typeof value === "string" ? value : JSON.stringify(value)
    }

    return {
      name,
      value: newCookieValue,
      domain: "localhost",
      path: "/",
      maxAge: 60 * 5,
    }
  })
  await context.addCookies(cookiesToSet)
}
