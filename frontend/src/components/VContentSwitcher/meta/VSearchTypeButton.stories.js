import { searchTypes } from "~/constants/media"
import useSearchType from "~/composables/use-search-type"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import VSearchTypeButton from "~/components/VContentSwitcher/VSearchTypeButton.vue"

const Template = (args) => ({
  template: `<VSearchTypeButton v-bind="args" v-on="args" />`,
  components: { VSearchTypeButton },
  setup() {
    const featureFlagStore = useFeatureFlagStore()
    featureFlagStore.toggleFeature("additional_search_types", "on")
    const st = useSearchType()
    st.setActiveType(args.searchType)
    args["aria-haspopup"] = "dialog"
    if (args.pressed) {
      args["aria-expanded"] = true
    }
    const searchTypeProps = st.getSearchTypeProps(args.searchType)
    return { args: { ...args, ...searchTypeProps } }
  },
})

export default {
  title: "Components/VContentSwitcher/VSearchTypeButton",
  components: VSearchTypeButton,

  argTypes: {
    searchType: {
      options: searchTypes,
      control: "select",
    },

    pressed: {
      control: "boolean",
    },

    showLabel: {
      control: "boolean",
    },

    click: {
      action: "click",
    },
  },

  args: {
    searchType: "all",
    pressed: false,
    showLabel: false,
  },
}

export const Default = {
  render: Template.bind({}),
  height: "480px",
  name: "Default",
}

export const LargePressedWithTextLabel = {
  render: Template.bind({}),
  height: "480px",
  name: "Large pressed with text label",

  args: {
    pressed: true,
    showLabel: true,
  },
}
