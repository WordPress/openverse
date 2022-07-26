<template>
  <button
    :aria-label="$t('browse-page.aria.scroll')"
    type="button"
    class="scroll fixed bottom-4 h-14 w-14 rounded-full bg-pink text-center text-white transition-all duration-100 ease-linear hover:bg-dark-pink hover:shadow-md"
    :class="hClass"
    @click="scrollToTop"
    @keydown.tab.exact="$emit('tab', $event)"
  >
    <svg
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
      class="h-full w-full fill-curr"
    >
      <path d="M6.5 12.4L12 8l5.5 4.4-.9 1.2L12 10l-4.5 3.6-1-1.2z" />
    </svg>
  </button>
</template>

<script lang="ts">
import { computed, defineComponent } from '@nuxtjs/composition-api'

import { defineEvent } from '~/types/emits'

const positionWithoutSidebar = 'ltr:right-4 rtl:left-4'
const positionWithSidebar = 'ltr:right-[21rem] rtl:left-[21rem]'

export default defineComponent({
  name: 'VScrollButton',
  props: {
    isFilterSidebarVisible: {
      type: Boolean,
      default: true,
    },
  },
  emits: {
    tab: defineEvent<[KeyboardEvent]>(),
  },
  setup(props) {
    const hClass = computed(() =>
      props.isFilterSidebarVisible
        ? positionWithSidebar
        : positionWithoutSidebar
    )
    const scrollToTop = () => {
      window.scrollTo({ top: 0, left: 0, behavior: 'smooth' })
    }
    return { hClass, scrollToTop }
  },
})
</script>
