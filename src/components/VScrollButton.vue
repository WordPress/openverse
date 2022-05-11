<template>
  <button
    :aria-label="$t('browse-page.aria.scroll')"
    type="button"
    class="scroll text-white bg-pink hover:bg-dark-pink transition-all duration-100 ease-linear fixed bottom-4 w-14 h-14 hover:shadow-md rounded-full text-center"
    :class="hClass"
    @click="scrollToTop"
    @keydown.tab.exact="$emit('tab', $event)"
  >
    <svg
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
      class="w-full h-full fill-curr"
    >
      <path d="M6.5 12.4L12 8l5.5 4.4-.9 1.2L12 10l-4.5 3.6-1-1.2z" />
    </svg>
  </button>
</template>

<script lang="ts">
import { computed, defineComponent } from '@nuxtjs/composition-api'

import { defineEvent } from '~/types/emits'

import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'

const positionWithoutSidebar = 'ltr:right-4 rtl:left-4'
const positionWithSidebar = 'ltr:right-[21rem] rtl:left-[21rem]'

export default defineComponent({
  name: 'VScrollButton',
  emits: {
    tab: defineEvent<[KeyboardEvent]>(),
  },
  setup() {
    const { isVisible: isFilterVisible } = useFilterSidebarVisibility()
    const hClass = computed(() =>
      isFilterVisible.value ? positionWithSidebar : positionWithoutSidebar
    )
    const scrollToTop = () => {
      window.scrollTo({ top: 0, left: 0, behavior: 'smooth' })
    }
    return { hClass, isFilterVisible, scrollToTop }
  },
})
</script>
