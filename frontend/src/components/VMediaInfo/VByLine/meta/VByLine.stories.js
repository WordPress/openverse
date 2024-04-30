import { supportedMediaTypes } from "~/constants/media"
import { useProviderStore } from "~/stores/provider"

import VByLine from "~/components/VMediaInfo/VByLine/VByLine.vue"

const Template = (args) => ({
  template: `<div class="wrapper w-full inline-flex p-4"><VByLine v-bind="args" /></div>`,
  components: { VByLine },
  setup() {
    const providerStore = useProviderStore()
    providerStore.getProviders().then(/** */)
    return { args }
  },
})

export default {
  title: "Components/VByLine",
  component: VByLine,

  argTypes: {
    mediaType: {
      control: "select",
      options: supportedMediaTypes,
    },

    creator: {
      control: "text",
    },

    sourceName: {
      control: "text",
    },

    sourceSlug: {
      control: "text",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "default",

  args: {
    mediaType: "image",
    creator: "kellascat",
    sourceSlug: "met",
    sourceName: "Metropolitan Museum",
  },
}

export const Long = {
  render: Template.bind({}),
  name: "long",

  args: {
    mediaType: "image",
    creator: "Roland Folger Coffin, American, 1826–1888",
    sourceSlug: "smithsonian_cooper_hewitt_museum",
    sourceName:
      "Smithsonian Institution: Cooper Hewitt, Smithsonian Design Museum",
  },
}
