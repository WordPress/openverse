<template>
  <VModalContent
    :aria-label="$t('header.aria.menu')"
    :hide-on-click-outside="true"
    :hide="close"
    :visible="visible"
    :variant="variant"
    class="flex items-center"
  >
    <VTabs
      :selected-id="selectedTab"
      tablist-style="ps-4 pe-2"
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
          ><VIcon :name="searchType.searchType" />
          <h2 class="label-regular">{{ $t("searchType.heading") }}</h2></VTab
        >
        <h2
          v-else
          class="label-regular relative my-2 me-4 flex h-12 items-center gap-x-2 px-2 after:absolute after:bottom-[-0.625rem] after:right-1/2 after:h-0.5 after:w-full after:translate-x-1/2 after:translate-y-[-50%] after:bg-dark-charcoal"
        >
          <VIcon :name="searchType.searchType" />
          {{ $t("searchType.heading") }}
        </h2>
        <VFilterTab
          v-if="showFilters"
          :applied-filter-count="appliedFilterCount"
        />
        <VIconButton
          :label="$t('modal.closeContentSettings')"
          :icon-props="{ name: 'close' }"
          variant="transparent-gray"
          size="large"
          class="ms-auto self-center"
          @click="close"
        />
      </template>
      <VTabPanel id="content-settings">
        <VSearchTypes
          size="medium"
          :use-links="useLinks"
          @select="$emit('select', $event)"
        />
      </VTabPanel>
      <!-- Horizontal padding removed to display divider. -->
      <!--<VTabPanel v-if="showFilters" id="filters" class="px-0">
        <VSearchGridFilter
          class="px-6"
          :show-filter-header="false"
          :change-tab-order="false"
        />
        <VSafeBrowsing class="border-t border-dark-charcoal-20 px-6 pt-6" />
      </VTabPanel>-->
    </VTabs>
    <!--<footer
      v-if="showFilters"
      class="mt-auto flex h-20 flex-shrink-0 items-center justify-between border-t border-t-dark-charcoal-20 p-4"
    >
      <VButton
        v-show="showClearFiltersButton"
        variant="transparent-gray"
        class="label-bold !text-pink disabled:!text-dark-charcoal-40"
        :disabled="isClearButtonDisabled"
        size="large"
        @click="clearFilters"
        >{{ $t("filterList.clear") }}
      </VButton>
      <VShowResultsButton :is-fetching="isFetching" @click="close" />
    </footer>-->
  </VModalContent>
</template>
<script lang="ts">
import { computed, defineComponent, PropType, ref } from "vue"

// import { useSearchStore } from "~/stores/search"

import useSearchType from "~/composables/use-search-type"

import { defineEvent } from "~/types/emits"

import { SearchType } from "~/constants/media"

// import VButton from "~/components/VButton.vue"
import VFilterTab from "~/components/VHeader/VHeaderMobile/VFilterTab.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VModalContent from "~/components/VModal/VModalContent.vue"
// import VSearchGridFilter from "~/components/VFilters/VSearchGridFilter.vue"
import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"
// import VShowResultsButton from "~/components/VHeader/VHeaderMobile/VShowResultsButton.vue"
import VTab from "~/components/VTabs/VTab.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"
import VTabs from "~/components/VTabs/VTabs.vue"
// import VSafeBrowsing from "~/components/VSafeBrowsing/VSafeBrowsing.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

type ContentSettingsTab = "content-settings" | "filters"

export default defineComponent({
  name: "VContentSettingsModalContent",
  components: {
    VIconButton,
    // VSafeBrowsing,
    VIcon,
    VModalContent,
    // VButton,
    VFilterTab,
    // VSearchGridFilter,
    VSearchTypes,
    // VShowResultsButton,
    VTab,
    VTabPanel,
    VTabs,
  },
  props: {
    variant: {
      type: String as PropType<"fit-content" | "two-thirds">,
      default: "fit-content",
    },
    isFetching: {
      type: Boolean,
      default: false,
    },
    close: {
      type: Function as PropType<() => void>,
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
  emits: {
    select: defineEvent<[SearchType]>(),
  },
  setup(props) {
    // const searchStore = useSearchStore()
    const content = useSearchType()
    const selectedTab = ref<ContentSettingsTab>("content-settings")
    const changeSelectedTab = (tab: string) => {
      selectedTab.value = tab as ContentSettingsTab
    }

    const areFiltersSelected = computed(() => {
      return false
      // return searchStore.isAnyFilterApplied
    })

    const showClearFiltersButton = computed(
      () => props.showFilters && selectedTab.value === "filters"
    )
    const isClearButtonDisabled = computed(() => {
      return false
      // return !searchStore.isAnyFilterApplied
    })
    const appliedFilterCount = computed<number>(() => {
      return 0
      // return searchStore.appliedFilterCount
    })

    const searchType = computed(() => content.getSearchTypeProps())

    const clearFilters = () => {
      // searchStore.clearFilters()
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
