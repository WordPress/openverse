import { ALL_LICENSES } from "~/constants/license"

import VLicenseElements from "~/components/VLicense/VLicenseElements.vue"

const Template = (args) => ({
  template: `<VLicenseElements v-bind="args" />`,
  components: { VLicenseElements },
  setup() {
    return { args }
  },
})

export default {
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

export const Big = {
  render: Template.bind({}),
  name: "Big",

  args: {
    license: "by-nc-nd",
  },
}

export const Small = {
  render: Template.bind({}),
  name: "Small",

  args: {
    license: "by-nc-nd",
    size: "small",
  },
}
