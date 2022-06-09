<template>
  <VButton
    id="filter-button"
    :variant="variant"
    size="disabled"
    class="self-center gap-2 align-center font-semibold py-2 flex-shrink-0 focus-visible:border-tx focus-visible:ring focus-visible:ring-pink"
    :class="
      filtersAreApplied
        ? 'px-3 flex-shrink-0'
        : 'w-10 md:w-auto h-10 md:h-auto px-0 md:px-3'
    "
    :pressed="pressed"
    :disabled="disabled"
    aria-controls="filters"
    :aria-label="mdMinLabel"
    @click="$emit('toggle')"
    @keydown.tab.exact="$emit('tab', $event)"
  >
    <VIcon
      :class="filtersAreApplied ? 'hidden' : 'block'"
      :icon-path="filterIcon"
    />
    <span class="hidden md:inline-block">{{ mdMinLabel }}</span>
    <span class="md:hidden" :class="!filtersAreApplied && 'hidden'">{{
      smMaxLabel
    }}</span>
  </VButton>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  inject,
  toRefs,
  ref,
} from '@nuxtjs/composition-api'

import { useSearchStore } from '~/stores/search'
import { defineEvent } from '~/types/emits'
import { useI18n } from '~/composables/use-i18n'

import VButton, { ButtonVariant } from '~/components/VButton.vue'
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
  setup(props) {
    const i18n = useI18n()
    const searchStore = useSearchStore()
    const { pressed } = toRefs(props)
    const isMinScreenMd = inject('isMinScreenMd', ref(false))
    const isHeaderScrolled = inject('isHeaderScrolled', ref(false))
    const filterCount = computed(() => searchStore.appliedFilterCount)
    const filtersAreApplied = computed(() => filterCount.value > 0)

    /**
     * Determine the visual style of the button
     * based on the viewport, the application of filters, and scrolling.
     */
    const variant = computed(() => {
      // Show the bordered state by default, unless below md
      let value: ButtonVariant = isMinScreenMd.value
        ? 'tertiary'
        : 'action-menu'

      if (isHeaderScrolled.value) {
        value = 'action-menu'
      }
      if (filtersAreApplied.value) {
        value = 'action-menu-muted'
      }
      // Override the default VButton pressed style
      if (pressed.value) {
        value = 'action-menu-muted-pressed'
      }
      return value
    })

    /**
     * This label's verbosity makes it useful for the aria-label
     * where it is also used, especially on mobile where the
     * label would just be the number of applied filters, and therefore
     * basically useless as far as a label is concerned!
     */
    const mdMinLabel = computed(() =>
      filtersAreApplied.value
        ? i18n.tc('header.filter-button.with-count', filterCount.value)
        : i18n.t('header.filter-button.simple')
    )

    const smMaxLabel = computed(() =>
      isHeaderScrolled.value
        ? filterCount.value
        : i18n.tc('header.filter-button.with-count', filterCount.value)
    )

    return {
      filterCount,
      filterIcon,
      mdMinLabel,
      smMaxLabel,
      variant,
      isHeaderScrolled,
      filtersAreApplied,
    }
  },
})
</script>
