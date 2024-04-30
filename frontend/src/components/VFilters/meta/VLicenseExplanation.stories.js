import { ALL_LICENSES } from "~/constants/license"

import VLicenseExplanation from "~/components/VFilters/VLicenseExplanation.vue"

const Template = (args) => ({
  template: `<VLicenseExplanation :license="args.license" v-bind="args" v-on="args"/>`,
  components: { VLicenseExplanation },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VLicenseExplanation",
  components: VLicenseExplanation,

  argTypes: {
    license: {
      options: ALL_LICENSES,
      control: "select",
    },
  },
  args: {
    license: ALL_LICENSES[0],
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
