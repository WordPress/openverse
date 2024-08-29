import { h } from "vue"

import { WithTeleportTarget } from "~~/.storybook/decorators/with-teleport-target"

import VHeaderMobile from "~/components/VHeader/VHeaderMobile/VHeaderMobile.vue"

import type { StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VHeader/VHeaderMobile/VHeaderMobile",
  component: VHeaderMobile,
  decorators: [WithTeleportTarget],
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VHeaderMobile },
    setup() {
      return () => h(VHeaderMobile, args)
    },
  }),
  name: "Default",
}
