import { useSearchStore } from "~/stores/search"
import { filterData, mediaFilterKeys } from "~/constants/filters"
import { IMAGE } from "~/constants/media"

import VFilterButton from "~/components/VHeader/VFilterButton.vue"

const Template = (args, { argTypes }) => ({
  template: `<div class="flex"><div id="wrapper" class="px-4 h-16 bg-bg-surface flex align-center justify-center">
  <VFilterButton v-bind="args" v-on="args" />
  </div></div>`,
  components: { VFilterButton },
  props: Object.keys(argTypes),
  setup() {
    const searchStore = useSearchStore()
    searchStore.setSearchType(IMAGE)
    function applyNFilters(filterCount) {
      searchStore.clearFilters()
      const filterTypes = [...mediaFilterKeys[IMAGE]]
      let filterIdx = 0
      // Skip license type filters as they can disable license filters
      let filterTypeIdx = 1
      for (let i = 0; i < filterCount; i++) {
        let filterType = filterTypes[filterTypeIdx]
        searchStore.toggleFilter({
          filterType,
          codeIdx: filterIdx,
        })
        filterIdx += 1
        if (filterData[filterType].length === filterIdx) {
          filterTypeIdx += 1
          filterIdx = 0
        }
      }
    }
    applyNFilters(args.appliedFilters)
    return { args }
  },
})

export default {
  title: "Components/VHeader/VFilterButton",
  component: VFilterButton,

  argTypes: {
    pressed: {
      type: "boolean",
    },

    appliedFilters: {
      type: "number",
    },

    disabled: {
      type: "boolean",
    },

    toggle: {
      action: "toggle",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  parameters: {
    viewport: {
      defaultViewport: "lg",
    },
  },
}

export const WithTextLabel = {
  render: Template.bind({}),
  name: "With text label",

  parameters: {
    viewport: {
      defaultViewport: "xl",
    },
  },
}
