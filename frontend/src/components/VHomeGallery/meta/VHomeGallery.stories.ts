import { h } from "vue"

import VHomeGallery from "~/components/VHomeGallery/VHomeGallery.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VHomeGallery",
  component: VHomeGallery,

  argTypes: {
    set: {
      options: ["random", "olympics", "pottery", "universe"],
      control: "select",
    },
  },
  args: {
    set: "random",
  },
} satisfies Meta<typeof VHomeGallery>

export default meta

export const Default: StoryObj<typeof meta> = {
  render: (args) => ({
    components: { VHomeGallery },
    setup() {
      return () => h(VHomeGallery, { ...args })
    },
  }),
  name: "Default",
}
