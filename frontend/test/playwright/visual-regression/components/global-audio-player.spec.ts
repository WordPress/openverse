import { test } from "@playwright/test"

import {
  languageDirections,
  pathWithDir,
  t,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import audio from "~~/test/playwright/utils/audio"

for (const dir of languageDirections) {
  breakpoints.describeXs(async ({ expectSnapshot }) => {
    test(`Global audio player on the search page - ${dir}`, async ({
      page,
    }) => {
      await preparePageForTests(page, "xs")
      await page.goto(
        pathWithDir("/search/audio/?q=honey&length=shortest", dir)
      )
      const audioRow = await audio.getNthAudioRow(page, 2)
      await audio.play(audioRow, dir)
      await page
        .locator(".global-track")
        .getByRole("button", { name: t("playPause.pause", dir) })
        .click()
      // To make the tests consistent, set the played area to the same position
      await page.mouse.click(170, 650)
      // Allow audio to buffer to the seeked position
      // eslint-disable-next-line playwright/no-networkidle
      await page.waitForLoadState("networkidle")
      await expectSnapshot(`global-audio-player-on-search-${dir}.png`, page)
    })
  })
}
