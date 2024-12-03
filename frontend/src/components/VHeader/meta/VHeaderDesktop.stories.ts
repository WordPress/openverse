import { h, provide, ref } from "vue"

import { IsSidebarVisibleKey } from "#shared/types/provides"

import VHeaderDesktop from "~/components/VHeader/VHeaderDesktop.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VHeader/VHeaderDesktop",
  component: VHeaderDesktop,
} satisfies Meta<typeof VHeaderDesktop>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => ({
    components: { VHeaderDesktop },
    setup() {
      provide(IsSidebarVisibleKey, ref(false))
      return () => h(VHeaderDesktop)
    },
  }),
  name: "Default",
}
