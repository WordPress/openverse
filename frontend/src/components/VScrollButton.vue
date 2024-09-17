<script setup lang="ts">
import { computed } from "vue"

import { useAnalytics } from "~/composables/use-analytics"
import { useSearchStore } from "~/stores/search"
import { useMediaStore } from "~/stores/media"

const positionWithoutSidebar = "ltr:right-4 rtl:left-4"
const positionWithSidebar = "ltr:right-[22rem] rtl:left-[22rem]"

const props = withDefaults(
  defineProps<{ isFilterSidebarVisible?: boolean }>(),
  { isFilterSidebarVisible: true }
)

const { sendCustomEvent } = useAnalytics()
const searchStore = useSearchStore()
const mediaStore = useMediaStore()
defineEmits<{ tab: [KeyboardEvent] }>()

const hClass = computed(() =>
  props.isFilterSidebarVisible ? positionWithSidebar : positionWithoutSidebar
)
const scrollToTop = (e: MouseEvent) => {
  const mainPage = document.getElementById("main-page")
  const element = mainPage || window
  element.scrollTo({ top: 0, left: 0, behavior: "smooth" })

  sendCustomEvent("BACK_TO_TOP", {
    query: searchStore.searchTerm,
    page: mediaStore.currentPage,
    scrollPixels: mainPage?.scrollTop || 0,
    maxScroll:
      mainPage && "scrollTopMax" in mainPage
        ? (mainPage.scrollTopMax as number)
        : 0,
  })
}
</script>

<template>
  <button
    :aria-label="$t('browsePage.aria.scroll')"
    type="button"
    class="scroll fixed bottom-4 mb-4 ms-auto h-14 w-14 rounded-full bg-primary text-center text-over-dark transition-all duration-100 ease-linear hover:bg-primary-hover hover:shadow-md"
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
