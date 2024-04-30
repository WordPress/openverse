import {
  CC_LICENSES,
  ALL_LICENSES,
  LICENSE_VERSIONS,
  PUBLIC_DOMAIN_MARKS,
  DEPRECATED_CC_LICENSES,
} from "~/constants/license"

import VMediaLicense from "~/components/VMediaInfo/VMediaLicense.vue"

const Template = (args) => ({
  template: `<VMediaLicense v-bind="args"/>`,
  components: { VMediaLicense },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VMediaLicense",
  component: VMediaLicense,

  argTypes: {
    license: {
      options: ALL_LICENSES,
      control: "select",
    },
    licenseVersion: {
      options: LICENSE_VERSIONS,
      control: "select",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
  inline: false,

  args: {
    license: ALL_LICENSES[0],
    licenseVersion: LICENSE_VERSIONS[0],
  },
}

export const PDM = {
  render: Template.bind({}),
  name: "PDM",
  args: {
    license: PUBLIC_DOMAIN_MARKS[0],
    licenseVersion: "1.0",
  },
}

export const CC0 = {
  render: Template.bind({}),
  name: "CC0",
  args: {
    license: PUBLIC_DOMAIN_MARKS[1],
    licenseVersion: "1.0",
  },
}

const getLicenseName = (license) => `CC ${license.toUpperCase()}`

export const CC_BY = {
  render: Template.bind({}),
  name: getLicenseName(CC_LICENSES[0]),
  args: {
    license: CC_LICENSES[0],
    licenseVersion: "4.0",
  },
}

export const CC_BY_SA = {
  render: Template.bind({}),
  name: getLicenseName(CC_LICENSES[1]),
  args: {
    license: CC_LICENSES[1],
    licenseVersion: "4.0",
  },
}

export const CC_BY_ND = {
  render: Template.bind({}),
  name: getLicenseName(CC_LICENSES[2]),
  args: {
    license: CC_LICENSES[2],
    licenseVersion: "4.0",
  },
}

export const CC_BY_NC = {
  render: Template.bind({}),
  name: getLicenseName(CC_LICENSES[3]),
  args: {
    license: CC_LICENSES[3],
    licenseVersion: "4.0",
  },
}

export const CC_BY_NC_SA = {
  render: Template.bind({}),
  name: getLicenseName(CC_LICENSES[4]),
  args: {
    license: CC_LICENSES[4],
    licenseVersion: "4.0",
  },
}

export const CC_BY_NC_ND = {
  render: Template.bind({}),
  name: getLicenseName(CC_LICENSES[5]),
  args: {
    license: CC_LICENSES[5],
    licenseVersion: "4.0",
  },
}

export const SAMPLING = {
  render: Template.bind({}),
  name: "CC Sampling+",
  args: {
    license: DEPRECATED_CC_LICENSES[1],
    licenseVersion: "1.0",
  },
}

export const NC_SAMPLING = {
  render: Template.bind({}),
  name: "CC NC-Sampling+",
  args: {
    license: DEPRECATED_CC_LICENSES[0],
    licenseVersion: "1.0",
  },
}
