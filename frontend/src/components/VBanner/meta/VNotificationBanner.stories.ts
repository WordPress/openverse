import { h } from "vue"

import { bannerNature } from "#shared/constants/banners"

import VNotificationBanner from "~/components/VBanner/VNotificationBanner.vue"

import type { StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VNotificationBanner",
  component: VNotificationBanner,

  argTypes: {
    nature: { control: "select", options: [...bannerNature] },
    variant: { control: "select", options: ["regular", "dark"] },
    onClose: { action: "close" },
  },
  args: {
    nature: "info",
    variant: "regular",
    id: "banner",
  },
}

export default meta
type Story = StoryObj<typeof meta>
type StoryTemplate = Omit<Story, "args">

const text =
  "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec justo eget felis facilisis fermentum."

const Template: StoryTemplate = {
  render: (args) => ({
    components: { VNotificationBanner },
    setup() {
      return () => h(VNotificationBanner, { ...args }, { default: () => text })
    },
  }),
}
export const Default = {
  ...Template,
  name: "Default",

  args: {
    nature: "success",
    variant: "regular",
  },
}

export const Dark = {
  ...Template,
  name: "Dark",

  args: {
    nature: "info",
    variant: "dark",
  },
}
