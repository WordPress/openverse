import VContentSettingsModalContent from "~/components/VHeader/VHeaderMobile/VContentSettingsModalContent.vue"
import VModalTarget from "~/components/VModal/VModalTarget.vue"

const Template = (args) => ({
  template: `<div><VContentSettingsModalContent v-bind="args" v-on="args" :close="args.close" /> <VModalTarget class="modal" /></div>`,
  components: { VContentSettingsModalContent, VModalTarget },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHeader/VHeaderMobile/VContentSettingsModalContent",
  components: VContentSettingsModalContent,

  argTypes: {
    visible: { type: "boolean" },
    close: { action: "close" },
    select: { action: "select" },
  },
  args: {
    visible: true,
  },
}

export const Default = {
  render: Template.bind({}),
  height: "480px",
  name: "Default",
}
