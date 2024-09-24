import { h } from "vue"

import AHeading from "~/components/ariakit/heading/AHeading.vue"

import AHeadingLevel from "~/components/ariakit/heading/AHeadingLevel.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Ariakit/Heading",
} satisfies Meta<typeof AHeading>

export default meta
type Story = StoryObj<typeof meta>

export const AHeadingStory: Story = {
  render: () => ({
    components: { AHeading, AHeadingLevel },
    setup() {
      return () =>
        h("div", { class: "wrapper" }, [
          h(AHeadingLevel, null, [
            h(AHeading, { class: "heading" }, ["First heading"]),
            h(AHeadingLevel, null, [
              h(AHeading, { as: { element: "div" } }, ["Second heading"]),
            ]),
          ]),
        ])
    },
  }),
}
