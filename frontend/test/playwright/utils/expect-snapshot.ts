import { expect } from "@playwright/test"

import { type LanguageDirection, t } from "~~/test/playwright/utils/i18n"

import type { Breakpoint } from "~/constants/screens"

import type {
  Expect,
  Locator,
  LocatorScreenshotOptions,
  Page,
  PageScreenshotOptions,
} from "@playwright/test"

export type ExpectSnapshotOptions = {
  screenshotOptions?: LocatorScreenshotOptions | PageScreenshotOptions
  snapshotOptions?: Parameters<ReturnType<Expect>["toMatchSnapshot"]>[0]
  dir?: LanguageDirection
  useColorMode?: boolean
}

export type ExpectSnapshot = <T extends Locator | Page>(
  page: Page,
  name: ReturnType<typeof getSnapshotBaseName>,
  screenshotAble: T,
  options?: ExpectSnapshotOptions
) => Promise<void>

export type ExpectScreenshotAreaSnapshot = (
  page: Page,
  name: string,
  options?: ExpectSnapshotOptions
) => Promise<void>

type EffectiveColorMode = "dark" | "light"
const themeSelectLabel = (dir: LanguageDirection) => t("theme.theme", dir)
const themeOption = (colorMode: EffectiveColorMode, dir: LanguageDirection) =>
  t(`theme.choices.${colorMode}`, dir)

export const turnOnDarkMode = async (page: Page, dir: LanguageDirection) => {
  // In Storybook, the footer story has two theme switchers (one in the footer, and one
  // is from the story decorator), so we need to select a single one.
  await page
    .getByLabel(themeSelectLabel(dir))
    .nth(0)
    .selectOption(themeOption("dark", dir))
}

type SnapshotNameOptions = {
  dir?: LanguageDirection
  breakpoint?: Breakpoint
}

const getSnapshotBaseName = (
  name: string,
  { dir, breakpoint }: SnapshotNameOptions = {}
) => {
  const dirString = dir ? (`-${dir}` as const) : ""
  const breakpointString = breakpoint ? (`-${breakpoint}` as const) : ""
  return `${name}${dirString}${breakpointString}` as const
}

const getSnapshotName = (
  name: ReturnType<typeof getSnapshotBaseName>,
  colorMode: EffectiveColorMode = "light"
) => {
  return `${name}-${colorMode}.png` as const
}

/**
 * Take a screenshot of the page or a given locator, and compare it to the existing snapshots.
 * Take a screenshot in both light and dark mode if `useColorMode` is true.
 */
export const expectSnapshot: ExpectSnapshot = async (
  page,
  name,
  screenshotAble,
  { screenshotOptions, snapshotOptions, useColorMode, dir } = {}
) => {
  // Hide the theme switcher before taking the screenshot.
  screenshotOptions = {
    ...(screenshotOptions ?? {}),
    style: `#storybook-theme-switcher {
              visibility: hidden;
            }`,
  }

  expect
    .soft(await screenshotAble.screenshot(screenshotOptions))
    .toMatchSnapshot(getSnapshotName(name, "light"), snapshotOptions)

  if (!(useColorMode === true)) {
    return
  }
  await turnOnDarkMode(page, dir ?? "ltr")

  expect(await screenshotAble.screenshot(screenshotOptions)).toMatchSnapshot(
    getSnapshotName(name, "dark"),
    snapshotOptions
  )
}

/**
 * Some component stories have a screenshot area that allows to take a snapshot
 * of the area around the component (for focus rings or complex stories with modals
 * or popovers).
 */
export const expectScreenshotAreaSnapshot: ExpectScreenshotAreaSnapshot =
  async (page, name, options = {}) => {
    return expectSnapshot(page, name, page.locator(".screenshot-area"), options)
  }
