import VBrand from "~/components/VBrand/VBrand.vue"

const Template = (args) => ({
  template: `<VBrand v-bind="args"/>`,
  components: { VBrand },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VBrand",
  component: VBrand,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}

export const Resized = {
  render: Template.bind({}),
  name: "Resized",

  args: {
    class: "text-6xl",
  },
}
