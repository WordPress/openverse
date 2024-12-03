import { h } from "vue"

import { ALL_LICENSES } from "#shared/constants/license"

import VLicenseExplanation from "~/components/VFilters/VLicenseExplanation.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VLicenseExplanation",
  component: VLicenseExplanation,

  argTypes: {
    license: {
      options: ALL_LICENSES,
      control: "select",
    },
  },
  args: {
    license: ALL_LICENSES[0],
  },
} satisfies Meta<typeof VLicenseExplanation>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VLicenseExplanation },
    setup() {
      return () => h(VLicenseExplanation, { ...args })
    },
  }),
  name: "Default",
}
