import { h } from "vue"

import { AUDIO, IMAGE } from "#shared/constants/media"
import { useMediaStore } from "~/stores/media"

import VLoadMore from "~/components/VLoadMore.vue"

import type { StoryObj } from "@storybook/vue3"

const Template: Story = {
  render: (args) => ({
    components: { VLoadMore },
    setup() {
      const mediaStore = useMediaStore()
      mediaStore.results[AUDIO] = {
        ...mediaStore.results[AUDIO],
        page: 1,
        pageCount: 12,
      }
      mediaStore.results[IMAGE] = {
        ...mediaStore.results[IMAGE],
        page: 1,
        pageCount: 12,
      }
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
