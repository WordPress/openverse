import { render } from '@testing-library/vue'

import Vue from 'vue'

import userEvent from '@testing-library/user-event'

import VTabs from '~/components/VTabs/VTabs.vue'
import VTab from '~/components/VTabs/VTab.vue'
import VTabPanel from '~/components/VTabs/VTabPanel.vue'

/**
 * Checks for visibility. We cannot check using `toBeVisible`
 * because visibility is set by Tailwind `hidden` class.
 * @param {import('@testing-library/vue').RenderResult } screen
 * @param {string} text
 * @param {boolean?} visibility
 */
const expectVisibitility = (screen, text, visibility = true) => {
  const classes = screen.getByText(text).getAttribute('class')
  return visibility
    ? expect(classes).not.toContain('hidden')
    : expect(classes).toContain('hidden')
}

const TestVTabsComponent = (manual = false) => {
  return Vue.component('VTabsComponent', {
    components: { VTabs, VTab, VTabPanel },
    data() {
      return { manual }
    },
    template: `<VTabs label="tabs" :manual="manual"><template #tabs>
      <VTab id='1'>Tab1</VTab><VTab id='2'>Tab2</VTab><VTab id='3'>Tab3</VTab>
    </template>
    <VTabPanel id='1'>Panel 1 content</VTabPanel>
    <VTabPanel id='2'>Panel 2 content</VTabPanel>
    <VTabPanel id='3'>Panel 3 content</VTabPanel>
    </VTabs>`,
  })
}

describe('VTabs', () => {
  it('should render default tabs', async () => {
    const screen = render(TestVTabsComponent())

    expect(screen.getByRole('tablist')).toHaveTextContent('Tab1Tab2Tab3')
    expect(screen.queryAllByRole('tab')).toHaveLength(3)
    expect(screen.queryAllByRole('tabpanel')).toHaveLength(3)

    /**
     * Panel visibility is set after the tabs and panels are registered
     * in `onMounted` and selectedIndex is set. This is why we need to wait
     * for the rendering using `nextTick`.
     */
    await Vue.nextTick()
    expectVisibitility(screen, 'Panel 1 content')
    expectVisibitility(screen, 'Panel 2 content', false)
    expectVisibitility(screen, 'Panel 3 content', false)
  })

  it('should change tabs on Right arrow press', async () => {
    const screen = render(TestVTabsComponent())

    await userEvent.click(screen.queryByText('Tab1'))
    await userEvent.keyboard('{ArrowRight}')

    expectVisibitility(screen, 'Panel 1 content', false)
    expectVisibitility(screen, 'Panel 2 content')
  })

  it('should change tabs on Right arrow and Enter press on manual activation', async () => {
    const screen = render(TestVTabsComponent(true))

    await userEvent.click(screen.queryByText('Tab1'))
    await userEvent.keyboard('{ArrowRight}')

    expectVisibitility(screen, 'Panel 1 content')
    expectVisibitility(screen, 'Panel 2 content', false)

    await userEvent.keyboard('{Enter}')

    expectVisibitility(screen, 'Panel 1 content', false)
    expectVisibitility(screen, 'Panel 2 content')
  })
})
