import type { Page } from "@playwright/test"

export const setViewportToFullHeight = async (page: Page) => {
  // Because of the overflow scroll, we cannot use `fullPage` screenshots.
  // Instead, we set the viewport to the full height of the page content.
  const viewportHeight = await page.evaluate(() => {
    const headerElHeight =
      document.querySelector(".header-el")?.clientHeight ?? 0

    // Get the height of the children of the "#main-page" element
    const mainPageChildren =
      document.getElementById("main-page")?.children ?? []
    const childHeight = Array.from(mainPageChildren).reduce(
      (acc, child) => acc + child.clientHeight,
      0
    )
    return childHeight + headerElHeight
  })

  const viewportWidth = page.viewportSize()?.width
  await page.setViewportSize({
    width: viewportWidth ?? 0,
    height: viewportHeight + 1,
  })
}
