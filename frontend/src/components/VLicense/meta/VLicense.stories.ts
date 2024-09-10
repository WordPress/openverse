import { h } from "vue"

import VLicense from "~/components/VLicense/VLicense.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VLicense",
  component: VLicense,
} satisfies Meta<typeof VLicense>

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VLicense },
    setup() {
      return () => h(VLicense, args)
    },
  }),
}

export const CcBy = {
  ...Template,
  name: "CC BY",

  args: {
    license: "by",
  },
}

export const CcBySa = {
  ...Template,
  name: "CC BY-SA",

  args: {
    license: "by-sa",
  },
}

export const CcByNd = {
  ...Template,
  name: "CC BY-ND",

  args: {
    license: "by-nd",
  },
}

export const CcByNc = {
  ...Template,
  name: "CC BY-NC",

  args: {
    license: "by-nc",
  },
}

export const CcByNcSa = {
  ...Template,
  name: "CC BY-NC-SA",

  args: {
    license: "by-nc-sa",
  },
}

export const CcByNcNd = {
  ...Template,
  name: "CC BY-NC-ND",

  args: {
    license: "by-nc-nd",
  },
}

export const Cc0 = {
  ...Template,
  name: "CC0",

  args: {
    license: "cc0",
  },
}

export const Pdm = {
  ...Template,
  name: "PDM",

  args: {
    license: "pdm",
  },
}

export const CcSampling = {
  ...Template,
  name: "CC Sampling+",

  args: {
    license: "sampling+",
  },
}

export const CcNcSampling = {
  ...Template,
  name: "CC NC-Sampling+",

  args: {
    license: "nc-sampling+",
  },
}

export const OnlyIcons = {
  ...Template,
  name: "Only icons",

  args: {
    license: "by-nc-sa",
    hideName: true,
  },
}
