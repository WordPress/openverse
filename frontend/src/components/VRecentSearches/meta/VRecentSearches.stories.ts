import { h } from "vue"

import VRecentSearches from "~/components/VRecentSearches/VRecentSearches.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VRecentSearches",
  component: VRecentSearches,

  argTypes: {
    onSelect: { action: "select" },

    onClear: { action: "clear" },

    "onLast-tab": { action: "last-tab" },
  },
} satisfies Meta<typeof VRecentSearches>

export default meta
type Story = StoryObj<typeof meta>

const Template: Story = {
  render: (args) => ({
    components: { VRecentSearches },
    setup() {
      return () => h(VRecentSearches, args)
    },
  }),
}

export const Default = {
  ...Template,
  name: "Default",

  args: {
    entries: ["addition", "subtraction", "multiplication", "division"],
  },
}

export const NoHistory = {
  ...Template,
  name: "No history",
}
