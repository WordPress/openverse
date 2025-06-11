import { expect } from "@playwright/test"
import { test } from "~~/test/playwright/utils/test"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import {
  goToSearchTerm,
  openFirstResult,
  pathWithDir,
  preparePageForTests,
  sleep,
} from "~~/test/playwright/utils/navigation"
import { languageDirections, t } from "~~/test/playwright/utils/i18n"

import { supportedMediaTypes } from "#shared/constants/media"

test.describe.configure({ mode: "parallel" })

for (const mediaType of supportedMediaTypes) {
  for (const dir of languageDirections) {
    breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
      test(`${mediaType} ${dir} single-result page snapshots from search results`, async ({
        page,
      }) => {
        await preparePageForTests(page, breakpoint)

        await page.route("**", (route) => {
          const url = route.request().url()
          // For audio, use the generated image instead of requesting the
          // thumbnail.
          if (
            url.endsWith(".jpg") ||
            (url.endsWith("/thumb/") && url.includes("/audio/"))
          ) {
            route.abort()
          } else {
            route.continue()
          }
        })

        await goToSearchTerm(page, "birds", { dir, mode: "SSR" })

        // This will include the "Back to results" link.
        await openFirstResult(page, mediaType, dir)
        // Wait for the rendering to finish.
        await expect(
          page.getByRole("link", {
            name: t(`${mediaType}Details.weblink`, dir),
          })
        ).toBeEnabled()

        await expectSnapshot(
          page,
          `${mediaType}-from-search-results-with-additional-search-views`,
          page,
          {
            dir,
            screenshotOptions: { fullPage: true },
            snapshotOptions: { maxDiffPixelRatio: 0.01 },
          }
        )
      })
    })
  }
}

for (const dir of languageDirections) {
  breakpoints.describeMobileAndDesktop(({ breakpoint, expectSnapshot }) => {
    test(`${dir} Sketchfab single result page snapshot`, async ({ page }) => {
      await preparePageForTests(page, breakpoint)

      const SKETCHFAB_ID = "da5cb478-c093-4d62-b721-cda18797e3fb"
      const path = pathWithDir(`/image/${SKETCHFAB_ID}`, dir)

      await page.goto(path)

      // Wait a bit for the Sketchfab iframe to fully load
      await sleep(3000)

      await expectSnapshot(
        `${dir}-sketchfab-single-result`,
        page,
        { fullPage: true },
        { maxDiffPixelRatio: 0.01 }
      )
    })
  })
}

for (const dir of languageDirections) {
  breakpoints.describeMobileAndDesktop(({ breakpoint, expectSnapshot }) => {
    test(`${dir} full-page report snapshots`, async ({ page }) => {
      await preparePageForTests(page, breakpoint)

      const IMAGE_ID = "da5cb478-c093-4d62-b721-cda18797e3fb"
      const path = pathWithDir(`/image/${IMAGE_ID}/report`, dir)

      await page.goto(path)

      // Wait for the language select to hydrate.
      await sleep(500)
      await expectSnapshot(page, "full-page-report", page, {
        dir,
        screenshotOptions: { fullPage: true },
        snapshotOptions: { maxDiffPixelRatio: undefined, maxDiffPixels: 2 },
      })
    })
  })
}
