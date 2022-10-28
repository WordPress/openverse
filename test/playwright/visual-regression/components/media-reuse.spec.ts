import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import {
  dismissTranslationBanner,
  languageDirections,
  pathWithDir,
  scrollDownAndUp,
  t,
} from '~~/test/playwright/utils/navigation'
import { mockProviderApis } from '~~/test/playwright/utils/route'

test.describe.configure({ mode: 'parallel' })

const tabs = [
  { id: 'rich', name: 'Rich Text' },
  { id: 'html', name: 'HTML' },
  { id: 'plain', name: 'Plain text' },
]

test.describe('media-reuse', () => {
  for (const tab of tabs) {
    for (const dir of languageDirections) {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test(`Should render a ${dir} media reuse section with "${tab.name}" tab open`, async ({
          context,
          page,
        }) => {
          await mockProviderApis(context)

          await page.goto(
            pathWithDir('/image/f9384235-b72e-4f1e-9b05-e1b116262a29', dir)
          )
          await dismissTranslationBanner(page)
          // The image is loading from provider, so we need to wait for it to
          // finish loaded to prevent the shift of the component during snapshots.
          await scrollDownAndUp(page)
          await page.waitForLoadState('networkidle')

          await page.locator(`#tab-${tab.id}`).click()
          // Make sure the tab is not focused and doesn't have a pink ring
          const reuseTitle = t('media-details.reuse.title', dir)
          await page.locator(`h2:has-text("${reuseTitle}")`).click()
          await expectSnapshot(
            `media-reuse-${dir}-${tab.id}-tab`,
            page.locator('.media-reuse')
          )
        })
      })
    }
  }
})
