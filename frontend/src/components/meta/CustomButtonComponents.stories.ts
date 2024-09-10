import { h } from "vue"

import { useMediaStore } from "~/stores/media"

import VLoadMore from "~/components/VLoadMore.vue"

import type { StoryObj } from "@storybook/vue3"

const Template: Story = {
  render: (args) => ({
    components: { VLoadMore },
    setup() {
      const mediaStore = useMediaStore()
      mediaStore._startFetching("image")
      mediaStore.results.image.count = 1
      return () =>
        h("div", { class: "flex p-4", id: "wrapper" }, [
          h(VLoadMore, {
            kind: "search",
            searchType: "image",
            searchTerm: "cat",
            isFetching: false,
            ...args,
          }),
        ])
    },
  }),
}

const meta = {
  title: "Components/CustomButtonComponents",
}

export default meta
type Story = StoryObj<typeof meta>

export const Default = {
  ...Template,
  name: "VLoadMore",

  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },
}
