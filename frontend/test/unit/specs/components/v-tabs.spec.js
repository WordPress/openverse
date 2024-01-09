import { createApp, nextTick } from "vue"

import { default as userEvent } from "@testing-library/user-event"

import { describe, expect, it } from "vitest"

import { render } from "~~/test/unit/test-utils/render"

import VTabs from "~/components/VTabs/VTabs.vue"
import VTab from "~/components/VTabs/VTab.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"

/**
 * To check visibility of the tab, we cannot use `toBeVisible`
 * because visibility is set by Tailwind `hidden` class.
 */
const classes = (screen, text) => screen.getByText(text).getAttribute("class")

const TestVTabsComponent = (manual = false) => {
  const componentWrapper = createApp({}).component("VTabsComponent", {
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
  return componentWrapper._context.components.VTabsComponent
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
    await nextTick()
    expect(classes(screen, "Panel 1 content")).not.toContain("hidden")
    expect(classes(screen, "Panel 2 content")).toContain("hidden")
    expect(classes(screen, "Panel 3 content")).toContain("hidden")
  })

  it("should change tabs on Right arrow press", async () => {
    const screen = await render(TestVTabsComponent())

    await userEvent.click(screen.queryByText("Tab1"))
    await userEvent.keyboard("{ArrowRight}")

    expect(classes(screen, "Panel 1 content")).toContain("hidden")
    expect(classes(screen, "Panel 2 content")).not.toContain("hidden")
  })

  it("should change tabs on Right arrow and Enter press on manual activation", async () => {
    const screen = await render(TestVTabsComponent(true))

    await userEvent.click(screen.queryByText("Tab1"))
    await userEvent.keyboard("{ArrowRight}")

    expect(classes(screen, "Panel 1 content")).not.toContain("hidden")
    expect(classes(screen, "Panel 2 content")).toContain("hidden")

    await userEvent.keyboard("{Enter}")

    expect(classes(screen, "Panel 1 content")).toContain("hidden")
    expect(classes(screen, "Panel 2 content")).not.toContain("hidden")
  })
})
