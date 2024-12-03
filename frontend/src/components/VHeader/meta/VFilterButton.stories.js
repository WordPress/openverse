import { h } from "vue"

import { filterData, mediaFilterKeys } from "#shared/constants/filters"
import { IMAGE } from "#shared/constants/media"
import { useSearchStore } from "~/stores/search"

import VFilterButton from "~/components/VHeader/VFilterButton.vue"

const meta = {
  title: "Components/VHeader/VFilterButton",
  component: VFilterButton,

  argTypes: {
    pressed: { type: "boolean" },

    appliedFilters: { type: "number" },

    disabled: { type: "boolean" },

    onToggle: { action: "toggle" },
  },
}

export default meta

const Template = (args) => ({
  components: { VFilterButton },
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
        const filterType = filterTypes[filterTypeIdx]
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
    return () =>
      h("div", { class: "flex" }, [
        h(
          "div",
          {
            id: "wrapper",
            class: "px-4 h-16 bg-surface flex align-center justify-center",
          },
          [h(VFilterButton, args)]
        ),
      ])
  },
})

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
