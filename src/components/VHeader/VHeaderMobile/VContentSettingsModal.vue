<template>
  <VModal
    ref="contentSettingsModalRef"
    :label="$t('header.aria.menu').toString()"
    :hide-on-click-outside="true"
    variant="two-thirds"
    class="flex items-center"
  >
    <template #trigger="{ visible, a11Props }">
      <VContentSettingsButton
        :is-pressed="visible"
        :applied-filter-count="appliedFilterCount"
        v-bind="a11Props"
      />
    </template>
    <VTabs
      :selected-id="selectedTab"
      tablist-style="ps-6 pe-2"
      variant="plain"
      label="content-settings"
      class="flex min-h-0 flex-col"
      @change="changeSelectedTab"
    >
      <template #tabs>
        <VTab id="content-settings" size="medium" class="category me-4">{{
          $t('search-type.heading')
        }}</VTab>
        <VTab id="filters" size="medium" class="category">{{
          $t('filters.title')
        }}</VTab>
        <VIconButton
          class="self-center ms-auto hover:bg-dark-charcoal hover:text-white"
          size="search-medium"
          :icon-props="{ iconPath: closeIcon }"
          :aria-label="$t('modal.aria-close')"
          @click="closeModal"
        />
      </template>
      <VTabPanel id="content-settings">
        <VSearchTypes size="medium" :use-links="true" />
      </VTabPanel>
      <VTabPanel id="filters">
        <VSearchGridFilter
          class="!p-0"
          :show-filter-header="false"
          :change-tab-order="false"
        />
      </VTabPanel>
    </VTabs>
    <footer
      class="mt-auto flex h-20 flex-shrink-0 items-center justify-between border-t border-t-dark-charcoal-20 px-6 py-4"
    >
      <VButton
        v-show="showClearFiltersButton"
        variant="text"
        :disabled="isClearButtonDisabled"
        @click="clearFilters"
        >{{ clearFiltersLabel }}
      </VButton>
      <VShowResultsButton :is-fetching="isFetching" @click="closeModal" />
    </footer>
  </VModal>
</template>
<script lang="ts">
import { computed, defineComponent, ref } from '@nuxtjs/composition-api'

import { useSearchStore } from '~/stores/search'

import { useI18n } from '~/composables/use-i18n'

import VButton from '~/components/VButton.vue'
import VContentSettingsButton from '~/components/VHeader/VHeaderMobile/VContentSettingsButton.vue'
import VIconButton from '~/components/VIconButton/VIconButton.vue'
import VModal from '~/components/VModal/VModal.vue'
import VSearchGridFilter from '~/components/VFilters/VSearchGridFilter.vue'
import VSearchTypes from '~/components/VContentSwitcher/VSearchTypes.vue'
import VShowResultsButton from '~/components/VHeader/VHeaderMobile/VShowResultsButton.vue'
import VTab from '~/components/VTabs/VTab.vue'
import VTabPanel from '~/components/VTabs/VTabPanel.vue'
import VTabs from '~/components/VTabs/VTabs.vue'

import closeIcon from '~/assets/icons/close-small.svg'

export default defineComponent({
  name: 'VContentSettingsModal',
  components: {
    VButton,
    VContentSettingsButton,
    VIconButton,
    VModal,
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
  },
  setup() {
    const contentSettingsModalRef = ref<InstanceType<typeof VModal> | null>(
      null
    )
    const i18n = useI18n()
    const searchStore = useSearchStore()
    const selectedTab = ref<'content-settings' | 'filters'>('content-settings')
    const changeSelectedTab = (tab: 'content-settings' | 'filters') => {
      selectedTab.value = tab
    }

    const areFiltersSelected = computed(() => searchStore.isAnyFilterApplied)

    const showClearFiltersButton = computed(
      () => selectedTab.value === 'filters'
    )
    const isClearButtonDisabled = computed(
      () => !searchStore.isAnyFilterApplied
    )
    const appliedFilterCount = computed(() => searchStore.appliedFilterCount)
    const clearFiltersLabel = computed(() =>
      searchStore.isAnyFilterApplied
        ? i18n.tc('filter-list.clear-numbered', appliedFilterCount.value)
        : i18n.t('filter-list.clear')
    )

    const clearFilters = () => {
      searchStore.clearFilters()
    }

    const closeModal = () => {
      contentSettingsModalRef.value?.close()
    }

    return {
      contentSettingsModalRef,
      closeIcon,
      closeModal,

      selectedTab,
      changeSelectedTab,

      areFiltersSelected,
      appliedFilterCount,
      showClearFiltersButton,
      isClearButtonDisabled,
      clearFiltersLabel,
      clearFilters,
    }
  },
})
</script>
