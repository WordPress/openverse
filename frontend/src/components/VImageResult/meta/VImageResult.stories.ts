import { h } from "vue"

import { image } from "~~/test/unit/fixtures/image"

import VImageResult from "~/components/VImageResult/VImageResult.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VImageResult",
  component: VImageResult,
} satisfies Meta<typeof VImageResult>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VImageResult },
    setup() {
      return () =>
        h("div", { class: "p-4 image-wrapper max-w-80" }, [
          h("ol", { class: "flex flex-wrap gap-4" }, [h(VImageResult, args)]),
        ])
    },
  }),
  name: "VImageResult",

  parameters: {
    viewport: { defaultViewport: "sm" },
  },

  argTypes: {
    aspectRatio: {
      options: ["square", "intrinsic"],
      control: { type: "select" },
    },
    image: { control: { type: "object" } },
  },

  args: {
    aspectRatio: "intrinsic",
    kind: "search",
    searchTerm: "test",
    relatedTo: "fake-uuid",

    image,
  },
}
