import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"

const Template = (args) => ({
  template: `<div class="fixed inset-0 w-full h-full"><VHeaderInternal v-bind="args" v-on="args" /><div id="modal"/></div>`,
  components: { VHeaderInternal },
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
