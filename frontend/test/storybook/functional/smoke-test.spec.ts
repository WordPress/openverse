import { expect, type Page, type Locator } from "@playwright/test"
import { test } from "~~/test/playwright/utils/test"

const checkPageLoaded = async (page: Page) => {
  await expect(
    page.getByRole("button", { name: "Remount component" })
  ).toBeVisible()
}

type Problem = {
  kind: "error" | "warning"
  message: string
  location: string
}

type StoryProblems = {
  count: number
  problems: Problem[]
}

const ignoredProblems = [
  /\[Plausible] Ignoring event because website is running locally/,
  /Failed to load resource: net::ERR_CONNECTION_REFUSED/,
  /Sentry DSN wasn't provided/,
  // Errors from the Storybook nuxt module
  // TypeError or Va
  /\[nuxt] error caught during app initialization \w*: Cannot read properties of undefined \(reading 'cdnURL'\)/,
  /Failed to load resource: the server responded with a status of 404 \(Not Found\)/,
  /\[Vue Router warn]: Record with path "\/iframe\.html" is either missing a "component\(s\)" or "children" property/,
]

const checkLink = async (page: Page, link: Locator) => {
  const linkHref = await link.getAttribute("href")
  if (!linkHref) {
    return
  }

  await link.click()
  await page.waitForURL(linkHref)
  await checkPageLoaded(page)

  await page.goBack()
}

const checkSection = async (
  page: Page,
  sectionButton: Locator,
  sectionId: string | null
) => {
  if (!sectionId) {
    return
  }
  if ((await sectionButton.getAttribute("aria-expanded")) === "false") {
    await sectionButton.click()
  }

  const directLinks = await page
    .locator(`a[data-parent-id="${sectionId}"]`)
    .all()
  for (const link of directLinks) {
    await checkLink(page, link)
  }

  const subsectionButtons = await page
    .locator(`button[data-parent-id="${sectionId}"]`)
    .all()
  for (const subsectionButton of subsectionButtons) {
    await checkSection(
      page,
      subsectionButton,
      await subsectionButton.getAttribute("id")
    )
  }
}

test.describe.configure({ timeout: 120000 })

test("Storybook renders without errors", async ({ page }) => {
  await page.goto("/")
  await checkPageLoaded(page)
  const problems: StoryProblems = { count: 0, problems: [] }

  page.on("console", async (msg) => {
    const consoleType = msg.type()
    if (
      ["warning", "error"].includes(consoleType) &&
      !ignoredProblems.some((pattern) => pattern.test(msg.text()))
    ) {
      problems.count += 1
      problems.problems.push({
        kind: consoleType as Problem["kind"],
        message: msg.text(),
        location: await page.title(),
      })
    }
  })

  const topLevelSections = await page
    .locator("#storybook-explorer-tree .sidebar-subheading")
    .all()

  for (const sectionHeadingLocator of topLevelSections) {
    const sectionButton = sectionHeadingLocator.locator("button").first()
    const sectionId = await sectionHeadingLocator.getAttribute("id")
    await checkSection(page, sectionButton, sectionId)
  }

  console.log("Problems", problems)
  expect(problems.count).toBe(0)
})
