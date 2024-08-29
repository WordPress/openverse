import { h } from "vue"

import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VHeader/VHeaderInternal",
  component: VHeaderInternal,
} as Meta<typeof VHeaderInternal>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VHeaderInternal },
    setup() {
      return () =>
        h("div", { id: "teleports" }, [
          h("div", { class: "fixed inset-0 w-full h-full" }, [
            h(VHeaderInternal, args),
          ]),
        ])
    },
  }),
  name: "Default",
}
