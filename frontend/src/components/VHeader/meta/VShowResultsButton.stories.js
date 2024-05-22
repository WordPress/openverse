import VShowResultsButton from "~/components/VHeader/VHeaderMobile/VShowResultsButton.vue"

const Template = (args) => ({
  template: `<VShowResultsButton v-bind="args"/>`,
  components: { VShowResultsButton },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHeader/VHeaderMobile/VShowResultsButton",
  component: VShowResultsButton,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}

export const Fetching = {
  render: Template.bind({}),
  name: "Fetching",

  args: {
    isFetching: true,
  },
}
