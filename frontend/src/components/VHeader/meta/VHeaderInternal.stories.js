import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"
import VModalTarget from "~/components/VModal/VModalTarget.vue"

const Template = (args) => ({
  template: `<div class="fixed inset-0 w-full h-full"><VHeaderInternal v-bind="args" v-on="args" /><VModalTarget /></div>`,
  components: { VHeaderInternal, VModalTarget },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHeader/VHeaderInternal",
  component: VHeaderInternal,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
