import VContentSettingsModalContent from "~/components/VHeader/VHeaderMobile/VContentSettingsModalContent.vue"

const Template = (args) => ({
  template: `<VContentSettingsModalContent v-bind="args" v-on="args" close="" />`,
  components: { VContentSettingsModalContent },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHeader/VHeaderMobile/VContentSettingsModalContent",
  components: VContentSettingsModalContent,

  argTypes: {
    close: {
      action: "close",
    },

    select: {
      action: "select",
    },

    change: {
      action: "change",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  height: "480px",
  name: "Default",
}
