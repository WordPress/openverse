import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"

const Template = (args) => ({
  template: `<VGridSkeleton v-bind="args" />`,
  components: { VGridSkeleton },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/Skeleton",
  component: VGridSkeleton,
}

export const AllTab = {
  render: Template.bind({}),
  name: "All tab",

  args: {
    isForTab: "all",
  },
}

export const ImageTab = {
  render: Template.bind({}),
  name: "Image tab",

  args: {
    isForTab: "image",
  },
}

export const AudioTab = {
  render: Template.bind({}),
  name: "Audio tab",

  args: {
    isForTab: "audio",
  },
}
