import { useFeatureFlagStore } from "~/stores/feature-flag"

import VSearchTypePopover from "~/components/VContentSwitcher/VSearchTypePopover.vue"

const Template = (args) => ({
  template: `<VSearchTypePopover active-item="image" v-bind="args" v-on="args"/>`,
  components: { VSearchTypePopover },
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
  title: "Components/VContentSwitcher/VSearchTypePopover",
  components: VSearchTypePopover,

  argTypes: {
    select: {
      action: "select",
    },

    additionalTypes: {
      control: {
        type: "boolean",
      },
    },
  },

  args: {
    additionalTypes: false,
  },
}

export const Default = {
  render: Template.bind({}),
  height: "480px",
  name: "Default",
}
