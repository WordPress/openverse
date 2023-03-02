<template>
  <section id="filters" aria-labelledby="filters-heading" class="filters">
    <header
      v-if="showFilterHeader"
      class="relative mb-6 flex items-center justify-between"
    >
      <h4 id="filters-heading" class="caption-bold uppercase">
        {{ $t("filter-list.filter-by") }}
      </h4>
      <VButton
        v-show="isAnyFilterApplied"
        id="clear-filter-button"
        variant="plain"
        class="label-bold absolute py-1 px-4 text-pink end-0 hover:ring hover:ring-pink"
        @click="clearFilters"
      >
        {{ $t("filter-list.clear") }}
      </VButton>
    </header>
    <form ref="filtersFormRef" class="filters-form">
      <template v-for="(filterType, index) in filterTypes">
        <!-- Divider above the sensitive content filter -->
        <div :key="index" class="relative">
          <div
            v-if="filterType === 'mature' && isSensitiveContentEnabled"
            :class="[isMobile ? 'mobileDividerLine' : 'desktopDividerLine']"
            class="absolute h-px bg-dark-charcoal-20"
          />
        </div>
        <VFilterChecklist
          :key="filterType"
          :options="filters[filterType]"
          :title="filterTypeTitle(filterType)"
          :filter-type="filterType"
          :class="[index === filterTypes.length - 2 ? 'mb-10' : 'mb-8']"
          @toggle-filter="toggleFilter"
        />
      </template>
    </form>
    <footer
      v-if="showFilterHeader && isAnyFilterApplied"
      class="flex justify-between md:hidden"
    >
      <VButton variant="primary" @click="$emit('close')">
        {{ $t("filter-list.show") }}
      </VButton>
    </footer>
  </section>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  ref,
  useContext,
  useRouter,
} from "@nuxtjs/composition-api"
import { kebab } from "case"

import { watchDebounced } from "@vueuse/core"

import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { areQueriesEqual, ApiQueryParams } from "~/utils/search-query-transform"
import type { FilterCategory } from "~/constants/filters"
import { defineEvent } from "~/types/emits"

import VFilterChecklist from "~/components/VFilters/VFilterChecklist.vue"
import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VSearchGridFilter",
  components: {
    VButton,
    VFilterChecklist,
  },
  props: {
    /**
     * Whether to show the header with the title and the clear button.
     */
    showFilterHeader: {
      type: Boolean,
      default: true,
    },
    /**
     * When the filters are in the sidebar, we change the keyboard tabbing order:
     * the focus moves from the Filters button to the filter,
     * and from the last tabbable element to the main content on Tab,
     * and from the filters to the filters button on Shift Tab.
     */
    changeTabOrder: {
      type: Boolean,
      default: true,
    },
  },
  emits: {
    close: defineEvent(),
  },
  setup() {
    const searchStore = useSearchStore()
    const featureFlagStore = useFeatureFlagStore()
    const uiStore = useUiStore()

    const { i18n } = useContext()
    const router = useRouter()

    const filtersFormRef = ref<HTMLFormElement>(null)

    const isAnyFilterApplied = computed(() => searchStore.isAnyFilterApplied)
    const filters = computed(() => searchStore.searchFilters)
    const filterTypes = computed(
      () => Object.keys(filters.value) as FilterCategory[]
    )
    const isMobile = computed(() => !uiStore.isDesktopLayout)
    const isSensitiveContentEnabled = computed(() =>
      featureFlagStore.isOn("toggle_sensitive_content")
    )

    const filterTypeTitle = (filterType: string) =>
      i18n.t(`filters.${kebab(filterType)}.title`)
    /**
     * This watcher fires even when the queries are equal. We update the path only
     * when the queries change.
     */
    watchDebounced(
      () => searchStore.searchQueryParams,
      (newQuery: ApiQueryParams, oldQuery: ApiQueryParams) => {
        if (!areQueriesEqual(newQuery, oldQuery)) {
          router.push(searchStore.getSearchPath())
        }
      },
      { debounce: 800, maxWait: 5000 }
    )

    return {
      filtersFormRef,
      isAnyFilterApplied,
      filters,
      filterTypes,
      filterTypeTitle,
      clearFilters: searchStore.clearFilters,
      toggleFilter: searchStore.toggleFilter,
      isMobile,
      isSensitiveContentEnabled,
    }
  },
})
</script>

<style scoped>
.mobileDividerLine {
  width: calc(100% + 3rem);
  left: -1.5rem;
}
.desktopDividerLine {
  width: calc(100% + 5rem);
  left: -2.5rem;
}
</style>
