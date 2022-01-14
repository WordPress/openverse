<template>
  <VButton
    :variant="variant"
    class="self-center gap-2 align-center font-semibold"
    :pressed="pressed"
    aria-controls="filter-sidebar"
    :aria-label="label"
    @click="toggleFilters"
  >
    <VIcon v-if="showIcon" :icon-path="filterIcon" />
    <span v-if="showLabel" data-testid="filterbutton-label">{{ label }}</span>
  </VButton>
</template>

<script>
import {
  computed,
  defineComponent,
  toRefs,
  useContext,
} from '@nuxtjs/composition-api'
import { isMinScreen } from '~/composables/use-media-query'
import filterIcon from '~/assets/icons/filter.svg'
import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon'

const VFilterButton = defineComponent({
  name: 'VFilterButton',
  components: {
    VIcon,
    VButton,
  },
  props: {
    /**
     * @default false
     */
    isHeaderScrolled: {
      type: Boolean,
      default: false,
    },
    pressed: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, { emit }) {
    const { i18n, store } = useContext()
    const { isHeaderScrolled, pressed } = toRefs(props)
    const isMinScreenMD = isMinScreen('md')

    const filterCount = computed(
      () => store.getters['search/appliedFilterTags'].length
    )
    const filtersAreApplied = computed(() => filterCount.value > 0)

    /**
     * Determine the visual style of the button
     * based on the viewport, the application of filters, and scrolling.
     */
    const variant = computed(() => {
      // Show the borderd state by default, unless below md
      let value = isMinScreenMD.value ? 'action-menu' : 'action-menu-secondary'

      if (isHeaderScrolled.value) {
        value = 'action-menu-secondary'
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
      if (!isMinScreenMD.value) {
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
     * Whether or not to show the filter icon,
     * based on viewport and the application of filters.
     */
    const showIcon = computed(() => {
      // When filters are applied, hide the icon
      if (filtersAreApplied.value) {
        return false
      }
      // Below the medium viewport, only show when there's no filters applied.
      if (!isMinScreenMD.value) {
        return !isHeaderScrolled.value || !filtersAreApplied.value
      }
      return true
    })

    // Hide the label entirely when no filters are applied on mobile.
    const showLabel = computed(() => {
      if (!isMinScreenMD.value && !filtersAreApplied.value) {
        return false
      }
      return true
    })

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
    }
  },
})

export default VFilterButton
</script>
