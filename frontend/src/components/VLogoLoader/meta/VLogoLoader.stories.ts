import { h } from "vue"

import VLink from "~/components/VLink.vue"
import VLogoLoader from "~/components/VLogoLoader/VLogoLoader.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VLogoLoader",
  component: VLogoLoader,

  argTypes: {
    status: {
      default: "idle",
      options: ["loading", "idle"],

      control: { type: "radio" },
    },
  },
} satisfies Meta<typeof VLogoLoader>

export default meta
type Story = StoryObj<typeof meta> & { args: { loadingLabel?: string } }

export const Idle: Story = {
  render: (args) => ({
    components: { VLogoLoader },
    setup() {
      return () => h(VLogoLoader, args)
    },
  }),
  name: "Idle",

  args: {
    status: "idle",
  },
}

export const Loading: Story = {
  render: (args) => ({
    components: { VLogoLoader },
    setup() {
      return () => h(VLogoLoader, args)
    },
  }),
  name: "Loading",

  args: {
    status: "loading",
    loadingLabel: "Loading images",
  },
}

export const Link: Story = {
  render: (args) => ({
    components: { VLink, VLogoLoader },
    setup() {
      return () =>
        h(
          VLink,
          { href: "https://wordpress.org/openverse" },
          { default: () => [h(VLogoLoader, args)] }
        )
    },
  }),
  name: "Link",

  args: {
    status: "loading",
    loadingLabel: "Loading images",
  },
}
