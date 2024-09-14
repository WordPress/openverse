import { h } from "vue"

import { WithScreenshotArea } from "~~/.storybook/decorators/with-screenshot-area"

import VLanguageSelect from "~/components/VLanguageSelect/VLanguageSelect.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VLanguageSelect",
  component: VLanguageSelect,
  decorators: [WithScreenshotArea],
} satisfies Meta<typeof VLanguageSelect>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VLanguageSelect },
    setup() {
      return () => h(VLanguageSelect, args)
    },
  }),
  name: "Default",
}
