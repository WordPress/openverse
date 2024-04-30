import VHeaderDesktop from "~/components/VHeader/VHeaderDesktop.vue"

const Template = (args) => ({
  template: `
    <VHeaderDesktop v-bind="args" v-on="args" />`,
  components: { VHeaderDesktop },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHeader/VHeaderDesktop",
  component: VHeaderDesktop,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
