import VLanguageSelect from "~/components/VLanguageSelect/VLanguageSelect.vue"

const Template = (args) => ({
  template: `
    <VLanguageSelect v-bind="args" />`,
  components: { VLanguageSelect },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VLanguageSelect",
  component: VLanguageSelect,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
