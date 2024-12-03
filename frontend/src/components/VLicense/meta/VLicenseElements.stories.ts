import { h } from "vue"

import { ALL_LICENSES } from "#shared/constants/license"

import VLicenseElements from "~/components/VLicense/VLicenseElements.vue"

import type { StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VLicenseElements",
  component: VLicenseElements,

  argTypes: {
    license: {
      default: "by",
      options: ALL_LICENSES,
      control: "select",
    },

    size: {
      default: "big",
      options: ["big", "small"],
      control: "select",
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VLicenseElements },
    setup() {
      return () => h(VLicenseElements, args)
    },
  }),
}

export const Big = {
  ...Template,
  name: "Big",

  args: {
    license: "by-nc-nd",
  },
}

export const Small = {
  ...Template,
  name: "Small",

  args: {
    license: "by-nc-nd",
    size: "small",
  },
}
