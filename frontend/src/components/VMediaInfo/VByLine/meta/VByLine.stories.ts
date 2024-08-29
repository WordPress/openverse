import { h } from "vue"

import { image as testImage } from "~~/test/unit/fixtures/image"

import VByLine from "~/components/VMediaInfo/VByLine/VByLine.vue"

import type { StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VByLine",
  component: VByLine,
}

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VByLine },
    setup() {
      return () =>
        h("div", { class: "wrapper w-full inline-flex p-4" }, [
          h(VByLine, args),
        ])
    },
  }),
}

export const Default = {
  ...Template,
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
  ...Template,
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
