import { h } from "vue"

import { image } from "~~/test/unit/fixtures/image"

import VImageCell from "~/components/VImageCell/VImageCell.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VImageCell",
  component: VImageCell,
} satisfies Meta<typeof VImageCell>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VImageCell },
    setup() {
      return () =>
        h("div", { class: "p-4 image-wrapper max-w-80" }, [
          h("ol", { class: "flex flex-wrap gap-4" }, [h(VImageCell, args)]),
        ])
    },
  }),
  name: "VImageCell",

  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },

  argTypes: {
    aspectRatio: {
      options: ["square", "intrinsic"],
      control: { type: "radio" },
    },

    image: {
      control: { type: "object" },
    },
  },

  args: {
    aspectRatio: "intrinsic",
    kind: "search",
    searchTerm: "test",
    relatedTo: "fake-uuid",

    image,
  },
}
