import VFooter from "~/components/VFooter/VFooter.vue"

const Template = (args) => ({
  template: '<VFooter v-bind="args" />',
  components: { VFooter },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VFooter",
  component: VFooter,
  parameters: {
    layout: "fullscreen",
  },
  height: "200px",
}

export const Content = {
  render: Template.bind({}),
  name: "Content",

  args: {
    mode: "content",
  },
}

export const Internal = {
  render: Template.bind({}),
  name: "Internal",

  args: {
    mode: "internal",
  },
}
