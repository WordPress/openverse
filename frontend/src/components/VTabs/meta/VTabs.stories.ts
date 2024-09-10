import { h } from "vue"

import VTabs from "~/components/VTabs/VTabs.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"
import VTab from "~/components/VTabs/VTab.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VTabs, VTabPanel, VTab },
    setup() {
      return () =>
        h(
          VTabs,
          { ...args },
          {
            tabs: () => [
              h(VTab, { id: "1" }, { default: () => "Tab1" }),
              h(VTab, { id: "2" }, { default: () => "Tab2" }),
              h(VTab, { id: "3" }, { default: () => "Tab3" }),
            ],
            default: () => [
              h(VTabPanel, { id: "1" }, { default: () => "Page 1 content" }),
              h(VTabPanel, { id: "2" }, { default: () => "Page 2 content" }),
              h(VTabPanel, { id: "3" }, { default: () => "Page 3 content" }),
            ],
          }
        )
    },
  }),
}
const meta = {
  component: VTabs,
  subcomponents: { VTabPanel, VTab },
  title: "Components/VTabs",

  argTypes: {
    variant: {
      options: ["bordered", "plain"],
      control: { type: "radio" },
    },

    onClose: { action: "close" },

    onChange: { action: "change" },
  },
} satisfies Meta<typeof VTabs>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  ...Template,
  name: "Default",

  args: {
    label: "Default tabs story",
    selectedId: "1",
  },
}

export const ManualPlainTabs: Story = {
  ...Template,
  name: "Manual plain tabs",

  args: {
    label: "Manual plain tabs",
    selectedId: "1",
    manual: true,
    variant: "plain",
  },
}
