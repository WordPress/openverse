import { test } from "@playwright/test"

import {
  dismissTranslationBanner,
  languageDirections,
  pathWithDir,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import audio from "~~/test/playwright/utils/audio"

for (const dir of languageDirections) {
  breakpoints.describeXs(async ({ expectSnapshot }) => {
    test(`Global audio player on the search page - ${dir}`, async ({
      page,
    }) => {
      await dismissTranslationBanner(page)
      await page.goto(
        pathWithDir("/search/audio/?q=honey&length=shortest", dir)
      )
      const audioRow = await audio.getNthAudioRow(page, 2)
      await audio.play(audioRow, dir)
      await audio.pause(audioRow, dir)
      // To make the tests consistent, set the played area to the same position
      await page.mouse.click(170, 650)
      await expectSnapshot(`global-audio-player-on-search-${dir}.png`, page)
    })
  })
}
