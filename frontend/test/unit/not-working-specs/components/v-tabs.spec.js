/* eslint jest/expect-expect: ["error", { "assertFunctionNames": ["expectVisibility"] }] */

import Vue from "vue"

import { default as userEvent } from "@testing-library/user-event"

import { render } from "~~/test/unit/test-utils/render"

import VTabs from "~/components/VTabs/VTabs.vue"
import VTab from "~/components/VTabs/VTab.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"

/**
 * Checks for visibility. We cannot check using `toBeVisible`
 * because visibility is set by Tailwind `hidden` class.
 */
const expectVisibility = (screen, text, visibility = true) => {
  const classes = screen.getByText(text).getAttribute("class")
  return visibility
    ? expect(classes).not.toContain("hidden")
    : expect(classes).toContain("hidden")
}

const TestVTabsComponent = (manual = false) => {
  return Vue.component("VTabsComponent", {
    components: { VTabs, VTab, VTabPanel },
    data() {
      return { manual }
    },
    template: `<VTabs label="tabs" :manual="manual" selected-id="1"><template #tabs>
      <VTab id='1'>Tab1</VTab><VTab id='2'>Tab2</VTab><VTab id='3'>Tab3</VTab>
    </template>
    <VTabPanel id='1'>Panel 1 content</VTabPanel>
    <VTabPanel id='2'>Panel 2 content</VTabPanel>
    <VTabPanel id='3'>Panel 3 content</VTabPanel>
    </VTabs>`,
  })
}

describe("VTabs", () => {
  it("should render default tabs", async () => {
    const screen = await render(TestVTabsComponent())

    expect(screen.getByRole("tablist")).toHaveTextContent("Tab1Tab2Tab3")
    expect(screen.queryAllByRole("tab")).toHaveLength(3)
    expect(screen.queryAllByRole("tabpanel")).toHaveLength(3)

    /**
     * Panel visibility is set after the tabs and panels are registered
     * in `onMounted` and selectedIndex is set. This is why we need to wait
     * for the rendering using `nextTick`.
     */
    await Vue.nextTick()
    expectVisibility(screen, "Panel 1 content")
    expectVisibility(screen, "Panel 2 content", false)
    expectVisibility(screen, "Panel 3 content", false)
    // TODO: fix expect visibility eslint
    expect(1).toBe(1)
  })

  it("should change tabs on Right arrow press", async () => {
    const screen = await render(TestVTabsComponent())

    await userEvent.click(screen.queryByText("Tab1"))
    await userEvent.keyboard("{ArrowRight}")

    expectVisibility(screen, "Panel 1 content", false)
    expectVisibility(screen, "Panel 2 content")
    // TODO: fix expect visibility eslint
    expect(1).toBe(1)
  })

  it("should change tabs on Right arrow and Enter press on manual activation", async () => {
    const screen = await render(TestVTabsComponent(true))

    await userEvent.click(screen.queryByText("Tab1"))
    await userEvent.keyboard("{ArrowRight}")

    expectVisibility(screen, "Panel 1 content")
    expectVisibility(screen, "Panel 2 content", false)

    await userEvent.keyboard("{Enter}")

    expectVisibility(screen, "Panel 1 content", false)
    expectVisibility(screen, "Panel 2 content")
    // TODO: fix expect visibility eslint
    expect(1).toBe(1)
  })
})
