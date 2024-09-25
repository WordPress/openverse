import { h } from "vue"

import ASeparator from "~/components/ariakit/separator/ASeparator.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Ariakit/Separator",
} satisfies Meta<typeof ASeparator>

export default meta
type Story = StoryObj<typeof meta>

export const AHeadingStory: Story = {
  render: () => ({
    components: { ASeparator },
    setup() {
      return () =>
        h("p", { class: "wrapper" }, [
          "Content before the separator",
          h(ASeparator, null, []),
          "Content after the separator",
        ])
    },
  }),
}

export const AHeadingAsStory: Story = {
  render: () => ({
    components: { ASeparator },
    setup() {
      return () =>
        h("p", { class: "wrapper" }, [
          "The separator below is rendered as a styled div",
          h(ASeparator, { as: "div", class: "border border-dashed" }, []),
          "If you inspect it, you'll see that AHeading set the correct role and aria attributes to make the div a separator",
        ])
    },
  }),
}
