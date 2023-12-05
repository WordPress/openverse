<template>
  <div
    ref="containerRef"
    class="relative -my-1.5px flex max-w-full sm:-ms-1"
    :class="{ 'pointer-events-none': !isInteractive }"
  >
    <div
      class="max-w-full"
      :class="{
        'faded-overflow-s': showScrollButton.start,
        'faded-overflow-e': showScrollButton.end,
      }"
    >
      <div
        ref="buttonsRef"
        class="buttons flex justify-start gap-x-3 overflow-x-scroll p-1.5px sm:gap-x-1"
        :class="{
          'ms-11': showScrollButton.start,
          'me-11': showScrollButton.end,
        }"
      >
        <VSourceCreatorButton
          v-if="showCreator && creatorHref && creator"
          :href="creatorHref"
          icon-name="person"
          :title="creator"
        />
        <VSourceCreatorButton
          :href="sourceHref"
          icon-name="institution"
          :title="sourceName"
        />
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

<script lang="ts">
import {
  computed,
  defineComponent,
  onMounted,
  PropType,
  reactive,
  ref,
} from "vue"
import { useElementSize, useScroll, watchDebounced } from "@vueuse/core"

import { useI18n } from "~/composables/use-i18n"
import type { SupportedMediaType } from "~/constants/media"

import VSourceCreatorButton from "~/components/VMediaInfo/VByLine/VSourceCreatorButton.vue"
import VScroller from "~/components/VMediaInfo/VByLine/VScroller.vue"

/**
 * A link to a collection page, either a source or a creator.
 */
export default defineComponent({
  name: "VByLine",
  components: {
    VScroller,
    VSourceCreatorButton,
  },
  props: {
    creator: {
      type: String,
    },
    sourceName: {
      type: String,
      required: true,
    },
    sourceSlug: {
      type: String,
      required: true,
    },
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
  },
  setup(props) {
    const containerRef = ref<HTMLElement | null>(null)
    const buttonsRef = ref<HTMLElement | null>(null)

    const showCreator = computed(() => {
      return props.creator && props.creator.toLowerCase() !== "unidentified"
    })

    const i18n = useI18n()
    const dir = computed(() => i18n.localeProperties.dir ?? "ltr")

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
      if (!buttonsRef.value || !containerRef.value) return
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

    const scroll = (to: "start" | "end") => {
      if (!buttonsRef.value) return
      const buttons = buttonsRef.value

      showScrollButton[to === "start" ? "end" : "start"] = true

      let distToSide = getDistToSide(to, dir.value, buttons)
      let adjustedScrollStep = scrollStep

      // If the scroll step is larger than the distance to the side, scroll
      // to the side and hide the scroll button.
      // If the distance to the side is less than twice the scroll step, scroll
      // half the distance to the side to prevent a very small scroll at the end.
      const isLastScroll = distToSide - scrollMargin <= scrollStep
      if (isLastScroll) {
        hideScrollButton(to)
        adjustedScrollStep = to === "start" ? distToSide : buttons.scrollWidth
      } else if (distToSide < scrollStep * 2) {
        adjustedScrollStep = distToSide / 2
      }
      if (dir.value === "rtl") {
        adjustedScrollStep = -adjustedScrollStep
      }

      let left = to === "start" ? -adjustedScrollStep : adjustedScrollStep
      buttons.scrollBy({ left, behavior: "smooth" })
    }

    watchDebounced(
      x,
      (xValue) => {
        if (!buttonsRef.value) return
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

    // TODO: implement this function in the search store.
    const getCollectionPath = ({
      type,
      source,
      creator,
    }: {
      type: SupportedMediaType
      source: string
      creator?: string
    }) => {
      let path = `/${type}/source/${source}/`
      if (creator) path += `creator/${encodeURIComponent(creator)}/`
      return path
    }
    const creatorHref = computed(() => {
      return showCreator.value
        ? getCollectionPath({
            type: props.mediaType,
            source: props.sourceSlug,
            creator: props.creator,
          })
        : undefined
    })
    const sourceHref = computed(() => {
      return getCollectionPath({
        type: props.mediaType,
        source: props.sourceSlug,
      })
    })

    return {
      containerRef,
      buttonsRef,

      showCreator,
      shouldScroll,
      showScrollButton,

      creatorHref,
      sourceHref,

      scroll,
      isInteractive,
    }
  },
})
</script>

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
