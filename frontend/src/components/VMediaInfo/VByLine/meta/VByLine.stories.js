import { image as testImage } from "~~/test/unit/fixtures/image"

import VByLine from "~/components/VMediaInfo/VByLine/VByLine.vue"

const Template = (args) => ({
  template: `<div class="wrapper w-full inline-flex p-4"><VByLine v-bind="args" /></div>`,
  components: { VByLine },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VByLine",
  component: VByLine,
}

export const Default = {
  render: Template.bind({}),
  name: "default",

  args: {
    media: {
      ...testImage,
      creator: "kellascat",
      sourceSlug: "met",
      sourceName: "Metropolitan Museum",
    },
  },
}

export const Long = {
  render: Template.bind({}),
  name: "long",

  args: {
    media: {
      ...testImage,
      creator: "Roland Folger Coffin, American, 1826–1888",
      sourceSlug: "smithsonian_cooper_hewitt_museum",
      sourceName:
        "Smithsonian Institution: Cooper Hewitt, Smithsonian Design Museum",
    },
  },
}
