import { h } from "vue"

import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/Skeleton",
  component: VGridSkeleton,
} satisfies Meta<typeof VGridSkeleton>

export default meta
type Story = StoryObj<typeof meta>

const Template: Story = {
  render: (args) => ({
    components: { VGridSkeleton },
    setup() {
      return () => h(VGridSkeleton, { isForTab: args.isForTab })
    },
  }),
}
export const AllTab: Story = {
  ...Template,
  name: "All tab",

  args: {
    isForTab: "all",
  },
}

export const ImageTab: Story = {
  ...Template,
  name: "Image tab",

  args: {
    isForTab: "image",
  },
}

export const AudioTab = {
  ...Template,
  name: "Audio tab",

  args: {
    isForTab: "audio",
  },
}
