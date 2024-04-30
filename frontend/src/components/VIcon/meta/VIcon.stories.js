import VIcon from "~/components/VIcon/VIcon.vue"

import spriteData from "~/assets/svg/sprite/sprites.json"

const iconNames = spriteData.reduce((accumulator, sprite) => {
  const iconsWithNamespace = sprite.symbols.map((symbol) =>
    sprite.defaultSprite ? symbol : `${sprite.name}/${symbol}`
  )
  return accumulator.concat(iconsWithNamespace)
}, [])

const Template = (args) => ({
  template: `<VIcon v-bind="args" />`,
  components: { VIcon },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VIcon",
  component: VIcon,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    name: "replay",
  },

  argTypes: {
    name: {
      options: iconNames,

      control: {
        type: "select",
      },
    },
  },
}

export const Rtl = {
  render: Template.bind({}),
  name: "RTL",

  args: {
    rtlFlip: true,
    name: "external-link",
  },
}
