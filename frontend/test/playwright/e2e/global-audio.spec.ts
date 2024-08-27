import { expect, test } from "@playwright/test"

import {
  goToSearchTerm,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import audio from "~~/test/playwright/utils/audio"
import { t } from "~~/test/playwright/utils/i18n"

test.describe.configure({ mode: "parallel" })

test.describe("global audio", () => {
  breakpoints.describeXs(() => {
    test.beforeEach(async ({ page }) => {
      await preparePageForTests(page, "xs")
      await page.routeFromHAR("./test/hars/global-audio-provider.har", {
        url: /wikimedia/,
        update: false,
      })
    })
    test("track continues playing when navigating from search to details page", async ({
      page,
    }) => {
      await goToSearchTerm(page, "honey", {
        searchType: "audio",
        query: "length=shortest",
      })

      // Find and play the first audio result
      const firstAudioRow = await audio.getNthAudioRow(page, 0)
      await audio.play(firstAudioRow)

      // Navigate to the details page of the playing audio track
      await firstAudioRow.click()

      // and confirm is still playing (or loading to play)
      const mainPlayerButton = page.locator(".main-track >> button").first()

      const labels = ["loading", "pause", "replay"].map((l) =>
        t(`playPause.${l}`)
      )
      const labelPattern = new RegExp(`(${labels.join("|")})`, "i")

      await expect(mainPlayerButton).toHaveAttribute("aria-label", labelPattern)
    })

    test("track can be closed while playing", async ({ page }) => {
      await goToSearchTerm(page, "honey", {
        searchType: "audio",
        query: "length=shortest",
      })

      // Find and play the first audio result
      const firstAudioRow = await audio.getNthAudioRow(page, 0)
      await audio.play(firstAudioRow)

      // Click in the middle of the player. After this, the player can be closed
      await page.mouse.click(170, 650)

      // Close the player
      await page
        .locator(".global-audio")
        .getByRole("button", { name: t("audioTrack.close") })
        .click()
      // and confirm the player is not visible
      await expect(page.locator(".global-audio")).toBeHidden()
    })

    test("player does not reproduce an audio different that the current audio in the details page", async ({
      page,
    }) => {
      await goToSearchTerm(page, "honey", {
        searchType: "audio",
        query: "length=shortest",
      })

      // Find and play the first audio result
      const firstAudioRow = await audio.getNthAudioRow(page, 0)
      await audio.play(firstAudioRow)
      // Navigate to the details page of the second audio track
      const secondAudioRow = await audio.getNthAudioRow(page, 1)
      await secondAudioRow.click()
      // and confirm is not playing
      await expect(
        page
          .locator(".main-track")
          .getByRole("button", { name: t("playPause.play") })
      ).toBeVisible()
    })
  })
})
