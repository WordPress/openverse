import { h } from "vue"

import VLogoButton from "~/components/VHeader/VLogoButton.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VHeader/HomeLinks/VLogoButton",
  component: VLogoButton,
} satisfies Meta<typeof VLogoButton>

export default meta

export const Default: StoryObj<typeof meta> = {
  render: (args) => ({
    components: { VLogoButton },
    setup() {
      return () => h("div", { class: "flex p-4" }, h(VLogoButton, { ...args }))
    },
  }),
  name: "Default",
}
