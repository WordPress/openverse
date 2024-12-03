import { supportedSearchTypes } from "#shared/constants/media"

import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/Skeleton",
  component: VGridSkeleton,
  argTypes: {
    isForTab: { control: "select", options: supportedSearchTypes },
  },
} satisfies Meta<typeof VGridSkeleton>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  name: "Grid Skeleton",
  args: {
    isForTab: "image",
  },
}
