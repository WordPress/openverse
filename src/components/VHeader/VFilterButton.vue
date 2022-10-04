<template>
  <VButton
    id="filter-button"
    :variant="filtersAreApplied ? 'action-menu-muted' : 'action-menu'"
    size="disabled"
    class="align-center label-regular h-12 w-12 gap-2 self-center xl:w-auto xl:ps-3"
    :class="[filtersAreApplied ? 'xl:pe-3' : 'xl:pe-4']"
    :pressed="pressed"
    :disabled="disabled"
    aria-controls="filters"
    :aria-label="xlMinLabel"
    @click="$emit('toggle')"
    @keydown.tab.exact="$emit('tab', $event)"
  >
    <VIcon
      :class="filtersAreApplied ? 'hidden' : 'block'"
      :icon-path="filterIcon"
    />
    <span class="hidden xl:inline-block">{{ xlMinLabel }}</span>
    <span class="xl:hidden" :class="{ hidden: !filtersAreApplied }">{{
      lgMaxLabel
    }}</span>
  </VButton>
</template>

<script lang="ts">
import { computed, defineComponent } from '@nuxtjs/composition-api'

import { useSearchStore } from '~/stores/search'
import { defineEvent } from '~/types/emits'
import { useI18n } from '~/composables/use-i18n'

import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'

import filterIcon from '~/assets/icons/filter.svg'

export default defineComponent({
  name: 'VFilterButton',
  components: {
    VIcon,
    VButton,
  },
  props: {
    pressed: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    tab: defineEvent<[KeyboardEvent]>(),
    toggle: defineEvent(),
  },
  setup() {
    const i18n = useI18n()
    const searchStore = useSearchStore()
    const filterCount = computed(() => searchStore.appliedFilterCount)
    const filtersAreApplied = computed(() => filterCount.value > 0)

    /**
     * This label's verbosity makes it useful for the aria-label
     * where it is also used, especially on mobile where the
     * label would just be the number of applied filters, and therefore
     * basically useless as far as a label is concerned!
     */
    const xlMinLabel = computed(() =>
      filtersAreApplied.value
        ? i18n.tc('header.filter-button.with-count', filterCount.value)
        : i18n.t('header.filter-button.simple')
    )
    const lgMaxLabel = computed(() =>
      filtersAreApplied ? filterCount.value : ''
    )

    return {
      filterIcon,
      xlMinLabel,
      lgMaxLabel,
      filtersAreApplied,
    }
  },
})
</script>
