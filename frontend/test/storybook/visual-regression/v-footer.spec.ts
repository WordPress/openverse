import { expect, Page } from "@playwright/test"
import { test } from "~~/test/playwright/utils/test"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import {
  type LanguageDirection,
  languageDirections,
} from "~~/test/playwright/utils/i18n"
import { dirParam } from "~~/test/storybook/utils/args"

const footerKinds = ["internal", "content"] as const

const storyUrl = (
  footerKind: (typeof footerKinds)[number],
  dir: LanguageDirection
) => `/iframe.html?id=components-vfooter--${footerKind}${dirParam(dir)}`

/**
 * TODO: Remove this when the theme selector is no longer highlighted.
 */
const disableNewHighlights = async (page: Page) => {
  const themeSwitcher = page.locator("#theme").nth(0)
  await themeSwitcher.click()
  await themeSwitcher.blur()
  await page.mouse.move(0, 0)
}

test.describe.configure({ mode: "parallel" })

test.describe("VFooter", () => {
  test("responds to available width without resizing the viewport", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1280, height: 700 })
    await page.goto(storyUrl("content", "ltr"))
    await expect(page.getByRole("combobox").nth(0)).toBeEnabled()

    const footer = page.locator("footer")
    const localeAndWp = footer.locator(".locale-and-wp")

    const layouts = [
      { width: 600, display: "flex", direction: "column" },
      { width: 800, display: "grid", direction: "column" },
      { width: 1100, display: "flex", direction: "row" },
      { width: 600, display: "flex", direction: "column" },
    ]

    for (const { width, display, direction } of layouts) {
      await footer.evaluate((element, width) => {
        element.parentElement!.style.width = `${width}px`
      }, width)

      await expect(localeAndWp).toHaveCSS("display", display)
      await expect(localeAndWp).toHaveCSS("flex-direction", direction)
    }
  })

  for (const dir of languageDirections) {
    for (const footerKind of footerKinds) {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test(`footer-${footerKind}-${dir}`, async ({ page }) => {
          await page.goto(storyUrl(footerKind, dir))

          // Ensure the component is hydrated by checking that language or theme select is enabled
          await expect(page.getByRole("combobox").nth(0)).toBeEnabled()
          await disableNewHighlights(page)

          await expectSnapshot(
            page,
            `footer-${footerKind}`,
            page.locator("footer"),
            { dir }
          )
        })
      })
    }
  }
})
