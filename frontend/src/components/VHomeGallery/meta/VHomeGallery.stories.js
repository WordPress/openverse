import VHomeGallery from "~/components/VHomeGallery/VHomeGallery.vue"

const Template = (args) => ({
  template: `<VHomeGallery v-bind="args" />`,
  components: { VHomeGallery },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHomeGallery",
  component: VHomeGallery,

  argTypes: {
    set: {
      options: ["random", "olympics", "pottery", "universe"],
      control: "select",
    },
  },
  args: {
    set: "random",
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
