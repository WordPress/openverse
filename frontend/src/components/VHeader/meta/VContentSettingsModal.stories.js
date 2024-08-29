import { h } from "vue"

import { WithTeleportTarget } from "~~/.storybook/decorators/with-teleport-target"

import VContentSettingsModalContent from "~/components/VHeader/VHeaderMobile/VContentSettingsModalContent.vue"

const meta = {
  title: "Components/VHeader/VHeaderMobile/VContentSettingsModalContent",
  component: VContentSettingsModalContent,

  parameters: {
    height: "480px",
  },

  decorators: [WithTeleportTarget],

  argTypes: {
    visible: { type: "boolean" },

    onClose: { action: "close" },

    onSelect: { action: "select" },
  },
  args: {
    visible: true,
  },
}
export default meta

export const Default = {
  render: (args) => ({
    components: { VContentSettingsModalContent },
    setup() {
      const close = () => console.log("close")

      return () =>
        h(VContentSettingsModalContent, {
          ...args,
          close,
        })
    },
  }),
  name: "Default",
}
