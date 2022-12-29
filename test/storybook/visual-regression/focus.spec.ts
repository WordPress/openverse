import { test, expect, Page, Locator } from "@playwright/test"

const goTo = async (page: Page, slug: string) => {
  await page.goto(`/iframe.html?id=meta-focus--${slug}`)
}

const expectSnapshot = async (name: string, elem: Locator) => {
  expect(await elem.screenshot()).toMatchSnapshot({ name: `${name}.png` })
}

const allSlugs = ["slim-transparent", "slim-filled", "bold-filled", "colored"]

test.describe.configure({ mode: "parallel" })

test.describe("Focus", () => {
  for (const slug of allSlugs) {
    test(`focus-${slug}`, async ({ page }) => {
      await goTo(page, slug)
      await page.focus('[data-testid="focus-target"]')
      await expectSnapshot(`focus-${slug}`, page.locator(".screenshot-area"))
    })
  }
})
