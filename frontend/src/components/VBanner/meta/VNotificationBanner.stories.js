import { h } from "vue"

import { bannerNature } from "#shared/constants/banners"

import VNotificationBanner from "~/components/VBanner/VNotificationBanner.vue"

const meta = {
  title: "Components/VNotificationBanner",
  component: VNotificationBanner,

  argTypes: {
    sNature: { control: "select", options: [...bannerNature] },
    sVariant: { control: "select", options: ["regular", "dark"] },
    onClose: { action: "close" },
  },
  args: {
    sNature: "info",
    sVariant: "regular",
    id: "banner",
  },
}

export default meta

const text =
  "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec justo eget felis facilisis fermentum."

const Template = {
  render: (args) => ({
    components: { VNotificationBanner },
    setup() {
      return () =>
        h(
          VNotificationBanner,
          { ...args, variant: args.sVariant, nature: args.sNature },
          { default: () => text }
        )
    },
  }),
}
export const Default = {
  ...Template,
  name: "Default",

  args: {
    sNature: "success",
    sVariant: "regular",
  },
}

export const Dark = {
  ...Template,
  name: "Dark",

  args: {
    sNature: "info",
    sVariant: "dark",
  },
}
