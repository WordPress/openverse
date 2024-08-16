import { expect, test } from "@playwright/test"

import { getH1 } from "~~/test/playwright/utils/components"
import { preparePageForTests } from "~~/test/playwright/utils/navigation"
import { t } from "~~/test/playwright/utils/i18n"

test.describe.configure({ mode: "parallel" })

test("sources table has links to source pages", async ({ page }) => {
  await preparePageForTests(page, "xl")
  await page.goto("/sources")
  await page
    .getByRole("cell", { name: "Flickr", exact: true })
    .getByRole("link")
    .click()
  await page.waitForURL("/image/collection?source=flickr")

  await expect(getH1(page, "Flickr")).toBeVisible()
})

// Tests the fix for https://github.com/WordPress/openverse/issues/4724
test("sources table can be sorted multiple times", async ({ page }) => {
  await preparePageForTests(page, "xl")
  await page.goto("/sources")

  const totalItems = page
    .getByRole("cell", { name: t("sources.providers.item") })
    .first()
  await totalItems.click()
  await totalItems.click()
  await totalItems.click()

  const firstRow = page.getByRole("row", { name: "Flickr" })
  await expect(firstRow).toBeVisible()
})
