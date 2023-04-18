<template>
  <VModalContent
    :aria-label="$t('header.aria.menu').toString()"
    :hide-on-click-outside="true"
    :hide="close"
    :visible="visible"
    :variant="showFilters ? 'two-thirds' : 'fit-content'"
    class="flex items-center"
  >
    <VTabs
      :selected-id="selectedTab"
      tablist-style="ps-6 pe-2"
      variant="plain"
      label="content-settings"
      class="flex min-h-0 flex-col"
      @change="changeSelectedTab"
    >
      <template #tabs>
        <VTab
          v-if="showFilters"
          id="content-settings"
          size="medium"
          class="me-4 gap-x-2"
          ><VIcon :icon-path="searchType.icon" />
          <h2 class="label-regular">{{ $t("search-type.heading") }}</h2></VTab
        >
        <h2
          v-else
          class="label-regular relative my-2 me-4 flex h-12 items-center gap-x-2 px-2 after:absolute after:bottom-[-0.625rem] after:right-1/2 after:h-0.5 after:w-full after:translate-x-1/2 after:translate-y-[-50%] after:bg-dark-charcoal"
        >
          <VIcon :icon-path="searchType.icon" />
          {{ $t("search-type.heading") }}
        </h2>
        <VFilterTab
          v-if="showFilters"
          :applied-filter-count="appliedFilterCount"
        />
        <VCloseButton
          :label="$t('modal.close-content-settings')"
          variant="filled-white"
          class="ms-auto self-center"
          @close="close"
        />
      </template>
      <VTabPanel id="content-settings">
        <VSearchTypes
          size="medium"
          :use-links="useLinks"
          @select="$emit('select', $event)"
        />
      </VTabPanel>
      <VTabPanel v-if="showFilters" id="filters">
        <VSearchGridFilter
          :show-filter-header="false"
          :change-tab-order="false"
        />
      </VTabPanel>
    </VTabs>
    <footer
      v-if="showFilters"
      class="mt-auto flex h-20 flex-shrink-0 items-center justify-between border-t border-t-dark-charcoal-20 px-6 py-4"
    >
      <VButton
        v-show="showClearFiltersButton"
        variant="text"
        class="!font-normal"
        :disabled="isClearButtonDisabled"
        @click="clearFilters"
        >{{ $t("filter-list.clear") }}
      </VButton>
      <VShowResultsButton :is-fetching="isFetching" @click="close" />
    </footer>
  </VModalContent>
</template>
<script lang="ts">
import { computed, defineComponent, ref } from "vue"

import { useSearchStore } from "~/stores/search"

import useSearchType from "~/composables/use-search-type"

import VButton from "~/components/VButton.vue"
import VCloseButton from "~/components/VCloseButton.vue"

import VFilterTab from "~/components/VHeader/VHeaderMobile/VFilterTab.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VModalContent from "~/components/VModal/VModalContent.vue"
import VSearchGridFilter from "~/components/VFilters/VSearchGridFilter.vue"
import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"
import VShowResultsButton from "~/components/VHeader/VHeaderMobile/VShowResultsButton.vue"
import VTab from "~/components/VTabs/VTab.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"
import VTabs from "~/components/VTabs/VTabs.vue"

export default defineComponent({
  name: "VContentSettingsModalContent",
  components: {
    VCloseButton,
    VIcon,
    VModalContent,
    VButton,
    VFilterTab,
    VSearchGridFilter,
    VSearchTypes,
    VShowResultsButton,
    VTab,
    VTabPanel,
    VTabs,
  },
  props: {
    isFetching: {
      type: Boolean,
      default: false,
    },
    close: {
      type: Function,
      required: true,
    },
    visible: {
      type: Boolean,
      default: false,
    },
    showFilters: {
      type: Boolean,
      default: true,
    },
    useLinks: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    const searchStore = useSearchStore()
    const content = useSearchType()
    const selectedTab = ref<"content-settings" | "filters">("content-settings")
    const changeSelectedTab = (tab: "content-settings" | "filters") => {
      selectedTab.value = tab
    }

    const areFiltersSelected = computed(() => searchStore.isAnyFilterApplied)

    const showClearFiltersButton = computed(
      () => props.showFilters && selectedTab.value === "filters"
    )
    const isClearButtonDisabled = computed(
      () => !searchStore.isAnyFilterApplied
    )
    const appliedFilterCount = computed<number>(
      () => searchStore.appliedFilterCount
    )

    const searchType = computed(() => content.getSearchTypeProps())

    const clearFilters = () => {
      searchStore.clearFilters()
    }

    return {
      searchType,

      selectedTab,
      changeSelectedTab,

      areFiltersSelected,
      appliedFilterCount,
      showClearFiltersButton,
      isClearButtonDisabled,
      clearFilters,
    }
  },
})
</script>
