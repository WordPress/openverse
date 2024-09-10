import { h } from "vue"

import VBackToSearchResultsLink from "~/components/VBackToSearchResultsLink.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VBackToSearchResultsLink",
  component: VBackToSearchResultsLink,
} satisfies Meta<typeof VBackToSearchResultsLink>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VBackToSearchResultsLink },
    setup() {
      return () => h(VBackToSearchResultsLink, args)
    },
  }),
  name: "Default",
  args: { id: "123", href: "#" },
}
