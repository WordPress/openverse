import VLink from "~/components/VLink.vue"
import VLogoLoader from "~/components/VLogoLoader/VLogoLoader.vue"

const Template = (args) => ({
  template: `<VLogoLoader v-bind="args" />`,
  components: { VLogoLoader },
  setup() {
    return { args }
  },
})

const LinkTemplate = (args) => ({
  template: `
    <VLink href="https://wordpress.org/openverse">
      <VLogoLoader v-bind="args" />
    </VLink>
  `,
  components: { VLink, VLogoLoader },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VLogoLoader",
  component: VLogoLoader,

  argTypes: {
    status: {
      default: "idle",
      options: ["loading", "idle"],

      control: {
        type: "radio",
      },
    },
  },
}

export const Idle = {
  render: Template.bind({}),
  name: "Idle",

  args: {
    status: "idle",
  },
}

export const Loading = {
  render: Template.bind({}),
  name: "Loading",

  args: {
    status: "loading",
    loadingLabel: "Loading images",
  },
}

export const Link = {
  render: LinkTemplate.bind({}),
  name: "Link",

  args: {
    status: "loading",
    loadingLabel: "Loading images",
  },
}
