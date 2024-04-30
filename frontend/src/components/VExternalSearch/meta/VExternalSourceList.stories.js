import { useSearchStore } from "~/stores/search"

import VExternalSourceList from "~/components/VExternalSearch/VExternalSourceList.vue"

const Template = (args) => ({
  template: `<VExternalSourceList search-term="cat" />`,
  components: { VExternalSourceList },
  setup() {
    const searchStore = useSearchStore()
    searchStore.setSearchType(args.type)
    return { args }
  },
})

export default {
  title: "Components/VExternalSourceList",
  component: VExternalSourceList,
}

export const Images = {
  render: Template.bind({}),
  name: "Images",
  args: { type: "image" },
}

export const Audio = {
  render: Template.bind({}),
  name: "Audio",
  args: { type: "audio" },
}

export const Video = {
  render: Template.bind({}),
  name: "Video",

  args: { type: "video" },
}

export const Model_3D = {
  render: Template.bind({}),
  name: "3D models",

  args: { type: "model-3d" },
}
