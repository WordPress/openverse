import { computed, h } from "vue"

import {
  CC_LICENSES,
  ALL_LICENSES,
  LICENSE_VERSIONS,
  PUBLIC_DOMAIN_MARKS,
  DEPRECATED_CC_LICENSES,
} from "~/constants/license"

import VMediaLicense from "~/components/VMediaInfo/VMediaLicense.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
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
} satisfies Meta<typeof VMediaLicense>

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VMediaLicense },
    setup() {
      const licenseUrl = computed(
        () =>
          `https://creativecommons.org/licenses/${args.license}/${args.licenseVersion}/`
      )
      return () => h(VMediaLicense, { ...args, licenseUrl: licenseUrl.value })
    },
  }),
}

export const Default = {
  ...Template,
  name: "Default",
  inline: false,

  args: {
    license: ALL_LICENSES[0],
    licenseVersion: LICENSE_VERSIONS[0],
  },
}

export const PDM = {
  ...Template,
  name: "PDM",
  args: {
    license: PUBLIC_DOMAIN_MARKS[0],
    licenseVersion: "1.0",
  },
}

export const CC0 = {
  ...Template,
  name: "CC0",
  args: {
    license: PUBLIC_DOMAIN_MARKS[1],
    licenseVersion: "1.0",
  },
}

const getLicenseName = (license: string) => `CC ${license.toUpperCase()}`

export const CC_BY = {
  ...Template,
  name: getLicenseName(CC_LICENSES[0]),
  args: {
    license: CC_LICENSES[0],
    licenseVersion: "4.0",
  },
}

export const CC_BY_SA = {
  ...Template,
  name: getLicenseName(CC_LICENSES[1]),
  args: {
    license: CC_LICENSES[1],
    licenseVersion: "4.0",
  },
}

export const CC_BY_ND = {
  ...Template,
  name: getLicenseName(CC_LICENSES[2]),
  args: {
    license: CC_LICENSES[2],
    licenseVersion: "4.0",
  },
}

export const CC_BY_NC = {
  ...Template,
  name: getLicenseName(CC_LICENSES[3]),
  args: {
    license: CC_LICENSES[3],
    licenseVersion: "4.0",
  },
}

export const CC_BY_NC_SA = {
  ...Template,
  name: getLicenseName(CC_LICENSES[4]),
  args: {
    license: CC_LICENSES[4],
    licenseVersion: "4.0",
  },
}

export const CC_BY_NC_ND = {
  ...Template,
  name: getLicenseName(CC_LICENSES[5]),
  args: {
    license: CC_LICENSES[5],
    licenseVersion: "4.0",
  },
}

export const SAMPLING = {
  ...Template,
  name: "CC Sampling+",
  args: {
    license: DEPRECATED_CC_LICENSES[1],
    licenseVersion: "1.0",
  },
}

export const NC_SAMPLING = {
  ...Template,
  name: "CC NC-Sampling+",
  args: {
    license: DEPRECATED_CC_LICENSES[0],
    licenseVersion: "1.0",
  },
}
