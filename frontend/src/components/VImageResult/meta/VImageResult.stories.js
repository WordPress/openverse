import { h } from "vue"

import { image } from "~~/test/unit/fixtures/image"

import VImageResult from "~/components/VImageResult/VImageResult.vue"

const meta = {
  title: "Components/VImageResult",
  component: VImageResult,
}
export default meta

export const Default = {
  render: (args) => ({
    components: { VImageResult },
    setup() {
      return () =>
        h("div", { class: "p-4 image-wrapper max-w-80" }, [
          h("ol", { class: "flex flex-wrap gap-4" }, [
            h(VImageResult, { ...args, aspectRatio: args.sAspectRatio }),
          ]),
        ])
    },
  }),
  name: "VImageResult",

  parameters: {
    viewport: { defaultViewport: "sm" },
  },

  argTypes: {
    sAspectRatio: {
      options: ["square", "intrinsic"],
      control: { type: "select" },
    },
    image: { control: { type: "object" } },
  },

  args: {
    sAspectRatio: "intrinsic",
    kind: "search",
    searchTerm: "test",
    relatedTo: "fake-uuid",

    image,
  },
}
