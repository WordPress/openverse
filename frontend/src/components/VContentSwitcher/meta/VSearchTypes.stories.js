import { h } from "vue"

import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"

const meta = {
  title: "Components/VContentSwitcher/VSearchTypes",
  component: VSearchTypes,

  parameters: {
    height: "480px",
    viewport: {
      defaultViewport: "sm",
    },
  },

  argTypes: {
    size: { options: ["small", "medium"], control: { type: "select" } },

    useLinks: { control: { type: "boolean" } },
  },

  args: {
    size: "medium",
    useLinks: false,
    additionalTypes: false,
  },
}

export default meta

export const Default = {
  render: (args) => ({
    components: { VSearchTypes },
    setup() {
      return () =>
        h(
          "div",
          {
            style: args.size === "small" ? "width: max-content;" : "",
            class: "wrapper p-2",
          },
          [h(VSearchTypes, args)]
        )
    },
  }),
  name: "Default",
}
