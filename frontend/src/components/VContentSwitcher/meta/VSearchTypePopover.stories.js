import { defineComponent, h } from "vue"

import { useFeatureFlagStore } from "~/stores/feature-flag"

import VSearchTypePopover from "~/components/VContentSwitcher/VSearchTypePopover.vue"

const meta = {
  title: "Components/VContentSwitcher/VSearchTypePopover",
  component: VSearchTypePopover,

  argTypes: {
    additionalTypes: { control: { type: "boolean" } },
    showLabel: { control: { type: "boolean" } },
  },

  parameters: {
    height: "480px",
  },
}
export default meta

const VSearchTypePopoverWrapper = defineComponent({
  name: "VSearchTypePopoverWrapper",
  components: { VSearchTypePopover },
  props: {
    additionalTypes: {
      type: Boolean,
      default: true,
    },
    showLabel: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    useFeatureFlagStore().toggleFeature(
      "additional_search_types",
      props.additionalTypes ? "on" : "off"
    )
    return () => h(VSearchTypePopover, { showLabel: props.showLabel })
  },
})

export const Default = {
  render: (args) => ({
    components: { VSearchTypePopoverWrapper },
    setup() {
      return () => h(VSearchTypePopoverWrapper, args)
    },
  }),
  name: "Default",
}
