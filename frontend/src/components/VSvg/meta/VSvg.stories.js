import VSvg from "~/components/VSvg/VSvg.vue"

import spriteData from "~/assets/svg/sprite/sprites.json"

const svgImages = spriteData.filter((sprite) => sprite.name === "images")[0]
  .symbols

const Template = (args) => ({
  template: `<VSvg v-bind="args" />`,
  components: { VSvg },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VSvg",
  component: VSvg,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    name: "wordpress",
    width: "100",
    height: "100",
  },

  argTypes: {
    name: {
      options: svgImages,

      control: {
        type: "select",
      },
    },

    viewbox: {
      control: {
        type: "text",
      },
    },

    width: {
      control: {
        type: "text",
      },
    },

    height: {
      control: {
        type: "text",
      },
    },
  },
}
