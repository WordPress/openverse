import VLicense from "~/components/VLicense/VLicense.vue"

const Template = (args) => ({
  template: `<VLicense v-bind="args" :license="args.license"/>`,
  components: { VLicense },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VLicense",
  component: VLicense,
}

export const CcBy = {
  render: Template.bind({}),
  name: "CC BY",

  args: {
    license: "by",
  },
}

export const CcBySa = {
  render: Template.bind({}),
  name: "CC BY-SA",

  args: {
    license: "by-sa",
  },
}

export const CcByNd = {
  render: Template.bind({}),
  name: "CC BY-ND",

  args: {
    license: "by-nd",
  },
}

export const CcByNc = {
  render: Template.bind({}),
  name: "CC BY-NC",

  args: {
    license: "by-nc",
  },
}

export const CcByNcSa = {
  render: Template.bind({}),
  name: "CC BY-NC-SA",

  args: {
    license: "by-nc-sa",
  },
}

export const CcByNcNd = {
  render: Template.bind({}),
  name: "CC BY-NC-ND",

  args: {
    license: "by-nc-nd",
  },
}

export const Cc0 = {
  render: Template.bind({}),
  name: "CC0",

  args: {
    license: "cc0",
  },
}

export const Pdm = {
  render: Template.bind({}),
  name: "PDM",

  args: {
    license: "pdm",
  },
}

export const CcSampling = {
  render: Template.bind({}),
  name: "CC Sampling+",

  args: {
    license: "sampling+",
  },
}

export const CcNcSampling = {
  render: Template.bind({}),
  name: "CC NC-Sampling+",

  args: {
    license: "nc-sampling+",
  },
}

export const OnlyIcons = {
  render: Template.bind({}),
  name: "Only icons",

  args: {
    license: "by-nc-sa",
    hideName: true,
  },
}
