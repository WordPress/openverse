<script setup lang="ts">
import { computed, ref } from "vue"

import { useSearchStore } from "~/stores/search"

import useSearchType from "~/composables/use-search-type"

import { SearchType } from "~/constants/media"

import VButton from "~/components/VButton.vue"
import VFilterTab from "~/components/VHeader/VHeaderMobile/VFilterTab.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VModalContent from "~/components/VModal/VModalContent.vue"
import VSearchGridFilter from "~/components/VFilters/VSearchGridFilter.vue"
import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"
import VShowResultsButton from "~/components/VHeader/VHeaderMobile/VShowResultsButton.vue"
import VTab from "~/components/VTabs/VTab.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"
import VTabs from "~/components/VTabs/VTabs.vue"
import VSafeBrowsing from "~/components/VSafeBrowsing/VSafeBrowsing.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

type ContentSettingsTab = "content-settings" | "filters"

const props = withDefaults(
  defineProps<{
    triggerElement?: HTMLElement | null
    variant?: "fit-content" | "two-thirds"
    isFetching?: boolean
    close: () => void
    visible?: boolean
    showFilters?: boolean
    useLinks?: boolean
  }>(),
  {
    triggerElement: null,
    variant: "fit-content",
    isFetching: false,
    visible: false,
    showFilters: true,
    useLinks: true,
  }
)

defineEmits<{
  select: [SearchType]
}>()

const searchStore = useSearchStore()
const content = useSearchType()
const selectedTab = ref<ContentSettingsTab>("content-settings")
const changeSelectedTab = (tab: string) => {
  selectedTab.value = tab as ContentSettingsTab
}

const showClearFiltersButton = computed(
  () => props.showFilters && selectedTab.value === "filters"
)
const isClearButtonDisabled = computed(() => !searchStore.isAnyFilterApplied)
const appliedFilterCount = computed<number>(
  () => searchStore.appliedFilterCount
)

const searchType = computed(() => content.getSearchTypeProps())

const clearFilters = () => {
  searchStore.clearFilters()
}
</script>

<template>
  <VModalContent
    :aria-label="$t('header.aria.menu')"
    :hide-on-click-outside="true"
    :hide="close"
    :visible="visible"
    :variant="variant"
    :trigger-element="triggerElement"
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
          class="label-regular relative my-2 me-4 flex h-12 items-center gap-x-2 px-2 after:absolute after:bottom-[-0.625rem] after:right-1/2 after:h-0.5 after:w-full after:translate-x-1/2 after:translate-y-[-50%] after:bg-tertiary"
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
      <VTabPanel v-if="showFilters" id="filters" class="px-0">
        <VSearchGridFilter
          class="px-6"
          :show-filter-header="false"
          :change-tab-order="false"
        />
        <VSafeBrowsing class="border-t border-default px-6 pt-6" />
      </VTabPanel>
    </VTabs>
    <footer
      v-if="showFilters"
      class="mt-auto flex h-20 flex-shrink-0 items-center justify-between border-t border-t-default p-4"
    >
      <VButton
        v-show="showClearFiltersButton"
        variant="transparent-gray"
        class="label-bold !text-link disabled:!text-disabled"
        :disabled="isClearButtonDisabled"
        size="large"
        @click="clearFilters"
        >{{ $t("filterList.clear") }}
      </VButton>
      <VShowResultsButton :is-fetching="isFetching" @click="close" />
    </footer>
  </VModalContent>
</template>
