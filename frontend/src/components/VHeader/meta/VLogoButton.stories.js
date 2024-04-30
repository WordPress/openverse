import VLogoButton from "~/components/VHeader/VLogoButton.vue"

const Template = (args) => ({
  template: `<div class="flex p-4"><VLogoButton v-bind="args" /></div>`,
  components: { VLogoButton },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHeader/HomeLinks/VLogoButton",
  component: VLogoButton,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
