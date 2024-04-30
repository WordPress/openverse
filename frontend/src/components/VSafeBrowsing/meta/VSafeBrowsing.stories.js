import VSafeBrowsing from "~/components/VSafeBrowsing/VSafeBrowsing.vue"

const Template = (args) => ({
  template: `<VSafeBrowsing v-bind="args" />`,
  components: { VSafeBrowsing },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VSafeBrowsing",
  component: VSafeBrowsing,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  // because it is present in the sidebar
  parameters: {
    viewport: {
      defaultViewport: "xs",
    },
  },
}
