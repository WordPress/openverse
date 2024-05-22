import VHeaderMobile from "~/components/VHeader/VHeaderMobile/VHeaderMobile.vue"

const Template = (args) => ({
  template: `
    <VHeaderMobile v-bind="args" v-on="args" />`,
  components: { VHeaderMobile },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHeader/VHeaderMobile/VHeaderMobile",
  component: VHeaderMobile,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
