import { useMediaStore } from "~/stores/media"

import VLoadMore from "~/components/VLoadMore.vue"

const Template = (args) => ({
  template: `
    <div id="wrapper" class="flex p-4"><VLoadMore kind="search" search-type="image" search-term="cat" :is-fetching="false" v-bind="args" /></div>
  `,
  components: { VLoadMore },
  setup() {
    const mediaStore = useMediaStore()
    mediaStore._startFetching("image")
    mediaStore.results.image.count = 1
    return { args }
  },
})

export default {
  title: "Components/CustomButtonComponents",
}

export const Default = {
  render: Template.bind({}),
  name: "VLoadMore",

  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },
}
