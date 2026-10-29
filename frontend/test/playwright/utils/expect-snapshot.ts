import { expect } from "@playwright/test"
import { type LanguageDirection, t } from "~~/test/playwright/utils/i18n"
import { sleep } from "~~/test/playwright/utils/navigation"
import { getThemeSwitcher } from "~~/test/playwright/utils/components"

import type { Breakpoint } from "#shared/constants/screens"

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

// Hide the theme switcher before taking the screenshot. The WordPress logo
// is hidden because its anti-aliasing differs between page loads.
export const snapshotHiddenStyle = `#storybook-theme-switcher, a[href="https://wordpress.org"] svg { visibility: hidden; }`

type EffectiveColorMode = "dark" | "light"
const themeOption = (colorMode: EffectiveColorMode, dir: LanguageDirection) =>
  t(`theme.choices.${colorMode}`, dir)

export const turnOnDarkMode = async (page: Page, dir: LanguageDirection) => {
  const themeSwitcher = getThemeSwitcher(page, dir)
  // Retry: a selection made before hydration finishes is lost or reset to "system".
  await expect(async () => {
    await themeSwitcher.selectOption({ label: themeOption("dark", dir) })
    await expect(themeSwitcher).toHaveValue("dark", { timeout: 1000 })
    await expect(page.locator("body")).toHaveClass(/\bdark-mode\b/, {
      timeout: 1000,
    })
  }).toPass({ timeout: 10_000 })
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
  { screenshotOptions, snapshotOptions, useColorMode = true, dir } = {}
) => {
  screenshotOptions = {
    ...(screenshotOptions ?? {}),
    style: snapshotHiddenStyle,
    animations: "disabled",
  }

  expect
    .soft(await screenshotAble.screenshot(screenshotOptions))
    .toMatchSnapshot(getSnapshotName(name, "light"), snapshotOptions)

  if (!useColorMode) {
    return
  }

  await turnOnDarkMode(page, dir ?? "ltr")

  // Wait for the theme to change.
  await sleep(100)

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
