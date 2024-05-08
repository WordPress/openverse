import { useFeatureFlagStore } from "~/stores/feature-flag"

import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"

const Template = (args) => ({
  template: `<VSearchTypes v-bind="args" v-on="args"/>`,
  components: { VSearchTypes },
  setup() {
    const featureFlagStore = useFeatureFlagStore()
    featureFlagStore.toggleFeature(
      "additional_search_types",
      args.additionalTypes ? "on" : "off"
    )
    return { args }
  },
})

export default {
  title: "Components/VContentSwitcher/VSearchTypes",
  components: VSearchTypes,

  argTypes: {
    size: {
      options: ["small", "medium"],

      control: {
        type: "select",
      },
    },

    useLinks: {
      control: {
        type: "boolean",
      },
    },

    additionalTypes: {
      control: {
        type: "boolean",
      },
    },
  },

  args: {
    size: "medium",
    useLinks: false,
    additionalTypes: false,
  },
}

export const Default = {
  render: Template.bind({}),
  height: "480px",
  name: "Default",
}
