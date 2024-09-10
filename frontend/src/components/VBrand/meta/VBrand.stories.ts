import { h } from "vue"

import VBrand from "~/components/VBrand/VBrand.vue"

import type { StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VBrand",
  component: VBrand,
}

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VBrand },
    setup() {
      return () => h(VBrand, args)
    },
  }),
}

export const Default = {
  ...Template,
  name: "Default",
}

export const Resized = {
  ...Template,
  name: "Resized",

  args: {
    class: "text-6xl",
  },
}
