import { expect, test } from "@playwright/test"

import { sleep, t } from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import audio from "~~/test/playwright/utils/audio"

test.describe("Global Audio", () => {
  breakpoints.describeXs(() => {
    test("track continues playing when navigating from search to details page", async ({
      page,
    }) => {
      await page.goto("/search/audio?q=honey&length=shortest")
      // Find and play the first audio result
      const firstAudioRow = await audio.getNthAudioRow(page, 0)
      await audio.play(firstAudioRow)
      // Navigate to the details page of the playing audio track
      await firstAudioRow.click()
      // and confirm is still playing (or loading to play)
      const mainPlayerButton = page.locator(".main-track >> button").first()
      await sleep(600) // Doesn't seem to make a difference for the status
      await expect(mainPlayerButton).toHaveAttribute(
        "aria-label",
        /(Loading|Pause|Replay)/
      )
    })

    test("track can be closed while playing", async ({ page }) => {
      await page.goto("/search/audio?q=honey")
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
      await page.goto("/search/audio?q=honey&length=shortest")
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
