import { ref } from "vue"

import VSnackbar from "~/components/VSnackbar.vue"

const Template = (args) => ({
  components: { VSnackbar },
  template: `
    <div>
      <input type="checkbox" id="show" v-model="isVisible">
      <label for="show">Show snackbar</label>
      <VSnackbar v-bind="args" :is-visible="isVisible">
        <template v-slot>${args.defaultSlot}</template>
      </Vsnackbar>
    </div>
  `,
  setup() {
    const isVisible = ref(true)
    return { args, isVisible }
  },
})

export default {
  title: "Components/VSnackbar",
  component: VSnackbar,

  argTypes: {
    size: {
      options: ["large", "small"],
      control: "radio",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
  inline: false,

  args: {
    defaultSlot: "Your message goes here.",
    size: "small",
  },
}
