<template>
  <VButton
    :variant="variant"
    size="disabled"
    class="self-center gap-2 align-center font-semibold py-2 flex-shrink-0 focus-visible:border-tx focus-visible:ring focus-visible:ring-pink"
    :class="{
      'px-3': !isIconButton,
      'w-10 h-10 px-0': isIconButton,
    }"
    :pressed="pressed"
    aria-controls="filter-sidebar"
    :aria-label="label"
    @click="toggleFilters"
  >
    <VIcon v-show="showIcon" :icon-path="filterIcon" />
    <span v-show="showLabel" data-testid="filterbutton-label">{{ label }}</span>
  </VButton>
</template>

<script>
import {
  computed,
  defineComponent,
  inject,
  toRefs,
  useContext,
} from '@nuxtjs/composition-api'

import { useSearchStore } from '~/stores/search'

import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'

import filterIcon from '~/assets/icons/filter.svg'

const VFilterButton = defineComponent({
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
  },
  setup(props, { emit }) {
    const { i18n } = useContext()
    const searchStore = useSearchStore()
    const { pressed } = toRefs(props)
    const isMinScreenMd = inject('isMinScreenMd', false)
    const isHeaderScrolled = inject('isHeaderScrolled', false)
    const filterCount = computed(() => searchStore.appliedFilterCount)
    const filtersAreApplied = computed(() => filterCount.value > 0)

    /**
     * Determine the visual style of the button
     * based on the viewport, the application of filters, and scrolling.
     */
    const variant = computed(() => {
      // Show the bordered state by default, unless below md
      let value = isMinScreenMd.value ? 'tertiary' : 'action-menu'

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

    const label = computed(() => {
      // Below medium viewport logic
      if (!isMinScreenMd.value) {
        return isHeaderScrolled.value
          ? filterCount.value
          : i18n.tc('header.filter-button.with-count', filterCount.value)
      }
      // Above the medium viewport, show the count when filters are applied.
      return filtersAreApplied.value
        ? i18n.tc('header.filter-button.with-count', filterCount.value)
        : i18n.t('header.filter-button.simple')
    })

    /**
     * Whether to show the filter icon,
     * based on viewport and the application of filters.
     */
    const showIcon = computed(() => {
      // When filters are applied, hide the icon
      if (filtersAreApplied.value) {
        return false
      }
      // Below the medium viewport, only show when there's no filters applied.
      if (!isMinScreenMd.value) {
        return !isHeaderScrolled.value || !filtersAreApplied.value
      }
      return true
    })

    // Hide the label entirely when no filters are applied on mobile.
    const showLabel = computed(() => {
      return !(!isMinScreenMd.value && !filtersAreApplied.value)
    })
    const isIconButton = computed(
      () =>
        !isMinScreenMd.value &&
        (!filtersAreApplied.value ||
          (filtersAreApplied.value && isHeaderScrolled.value))
    )
    return {
      filterCount,
      filterIcon,
      label,
      showIcon,
      showLabel,
      toggleFilters: () => {
        emit('toggle')
      },
      variant,
      isMinScreenMd,
      isHeaderScrolled,
      isIconButton,
    }
  },
})

export default VFilterButton
</script>
