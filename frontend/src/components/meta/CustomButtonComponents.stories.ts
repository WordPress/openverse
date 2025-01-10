import { h } from "vue"

import VLoadMore from "~/components/VLoadMore.vue"

import type { StoryObj } from "@storybook/vue3"

const Template: Story = {
  render: (args) => ({
    components: { VLoadMore },
    setup() {
      return () =>
        h("div", { class: "flex p-4", id: "wrapper" }, [
          h(VLoadMore, {
            kind: "search",
            searchType: "image",
            searchTerm: "cat",
            isFetching: false,
            canLoadMore: true,
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
