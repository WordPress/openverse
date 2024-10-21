<script setup lang="ts">
/**
 * A link to a collection page, either a source or a creator.
 */
import { useI18n } from "#imports"

import { computed, onMounted, reactive, ref } from "vue"
import { useElementSize, useScroll, watchDebounced } from "@vueuse/core"

import VScroller from "~/components/VMediaInfo/VByLine/VScroller.vue"

const containerRef = ref<HTMLElement | null>(null)
const buttonsRef = ref<HTMLElement | null>(null)
const innerContainerRef = ref<HTMLElement | null>(null)

const { localeProperties } = useI18n({ useScope: "global" })
const dir = computed(() => localeProperties.value.dir ?? "ltr")

const scrollStep = 150 // px to scroll on each click
const scrollMargin = 44 // px, button + margin
const shouldScroll = ref(false)

const { x } = useScroll(buttonsRef)
const { width: containerWidth } = useElementSize(containerRef)

const showScrollButton = reactive({
  start: false,
  end: false,
})
const setScrollable = () => {
  shouldScroll.value = true
  showScrollButton.start = false
  showScrollButton.end = true
}

const hideScrollButton = (side: "start" | "end") => {
  showScrollButton[side] = false
  isInteractive.value = false
  setTimeout(() => {
    isInteractive.value = true
  }, 500)
}
const isInteractive = ref(true)

watchDebounced(
  containerWidth,
  (cWidth) => {
    const buttonsScrollWidth = buttonsRef.value?.scrollWidth ?? 0
    const hasOverflow = buttonsScrollWidth >= cWidth
    if (hasOverflow && !shouldScroll.value) {
      setScrollable()
    } else if (!hasOverflow && shouldScroll.value) {
      shouldScroll.value = false
      showScrollButton.start = false
      showScrollButton.end = false
    }
  },
  { debounce: 500 }
)

onMounted(() => {
  if (!buttonsRef.value || !containerRef.value) {
    return
  }
  if (buttonsRef.value?.scrollWidth > containerRef.value.scrollWidth) {
    setScrollable()
  }
})

const getScrollEnd = (el: HTMLElement, dir: "ltr" | "rtl" | "auto") => {
  return (
    el.scrollWidth -
    el.clientWidth -
    (dir === "rtl" ? -el.scrollLeft : el.scrollLeft)
  )
}
const getScrollStart = (el: HTMLElement) => {
  return Math.abs(el.scrollLeft)
}

const getDistToSide = (
  to: "start" | "end",
  dir: "ltr" | "rtl" | "auto",
  el: HTMLElement
) => {
  return to === "start" ? getScrollStart(el) : getScrollEnd(el, dir)
}

const scrollToSide = ({ side }: { side: "start" | "end" }) => {
  hideScrollButton(side)
  if (!buttonsRef.value) {
    return
  }
  const left =
    side === "start"
      ? 0
      : dir.value === "ltr"
        ? buttonsRef.value.scrollWidth
        : -buttonsRef.value.scrollWidth
  buttonsRef.value.scrollTo({ left, behavior: "smooth" })
}

const scroll = (to: "start" | "end") => {
  if (!buttonsRef.value || !innerContainerRef.value) {
    return
  }
  const innerContainer = innerContainerRef.value

  showScrollButton[to === "start" ? "end" : "start"] = true

  const distToSide = getDistToSide(to, dir.value, innerContainer)
  let adjustedScrollStep = scrollStep

  // If the scroll step is larger than the distance to the side, scroll
  // to the side and hide the scroll button.
  // If the distance to the side is less than twice the scroll step, scroll
  // half the distance to the side to prevent a very small scroll at the end.
  const isLastScroll = distToSide - scrollMargin <= scrollStep
  if (isLastScroll) {
    scrollToSide({ side: to })
    return
  }
  if (distToSide < scrollStep * 2) {
    adjustedScrollStep = distToSide / 2
  }
  if (dir.value === "rtl") {
    adjustedScrollStep = -adjustedScrollStep
  }

  const left = to === "start" ? -adjustedScrollStep : adjustedScrollStep
  buttonsRef.value?.scrollBy({ left, behavior: "smooth" })
}

watchDebounced(
  x,
  (xValue) => {
    if (!buttonsRef.value) {
      return
    }
    // This is necessary for handling both RTL and LTR.
    const distFromStart = Math.abs(xValue)
    const distFromEnd =
      buttonsRef.value.scrollWidth -
      distFromStart -
      buttonsRef.value.clientWidth
    showScrollButton.start = distFromStart >= scrollMargin
    showScrollButton.end = distFromEnd >= scrollMargin
  },
  { debounce: 100 }
)
</script>

<template>
  <div
    ref="containerRef"
    class="container relative flex min-w-0"
    :class="{ 'pointer-events-none': !isInteractive }"
  >
    <div
      ref="innerContainerRef"
      class="inner-container max-w-full"
      :class="{
        'faded-overflow-s': showScrollButton.start,
        'faded-overflow-e': showScrollButton.end,
      }"
    >
      <div
        ref="buttonsRef"
        class="buttons flex justify-start gap-x-3 overflow-x-scroll sm:gap-x-1"
        :class="[
          showScrollButton.start
            ? showScrollButton.end
              ? 'me-11 ms-11 w-[calc(100%_-_2_*_theme(spacing.11))]'
              : 'ms-11 w-[calc(100%_-_theme(spacing.11))]'
            : showScrollButton.end
              ? 'me-11 w-[calc(100%_-_theme(spacing.11))]'
              : '',
        ]"
      >
        <slot />
      </div>
    </div>
    <VScroller
      v-show="showScrollButton.start"
      class="start-0"
      direction="back"
      @click="scroll('start')"
    />
    <VScroller
      v-show="showScrollButton.end"
      class="end-0"
      direction="forward"
      @click="scroll('end')"
    />
  </div>
</template>

<style scoped>
.buttons::-webkit-scrollbar {
  width: 0 !important;
  height: 0 !important;
}
.buttons {
  scrollbar-width: none;
}

.faded-overflow-e:dir(ltr),
.faded-overflow-s:dir(rtl) {
  mask-image: linear-gradient(
    to left,
    transparent 0,
    transparent 44px,
    #000 98px,
    #000 100%
  );
}
.faded-overflow-e:dir(rtl),
.faded-overflow-s:dir(ltr) {
  mask-image: linear-gradient(
    to right,
    transparent 0,
    transparent 44px,
    #000 98px,
    #000 100%
  );
}

.faded-overflow-e.faded-overflow-s {
  mask-image: linear-gradient(
      to right,
      transparent 0,
      transparent 44px,
      #000 98px,
      #000 50%,
      transparent 50%,
      transparent 100%
    ),
    linear-gradient(
      to left,
      transparent 0,
      transparent 44px,
      #000 98px,
      #000 50%,
      transparent 50%,
      transparent 100%
    );
}
</style>
