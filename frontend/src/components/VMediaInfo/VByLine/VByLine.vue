<template>
  <div ref="containerRef" class="relative flex max-w-full sm:-ms-1">
    <div
      class="max-w-full"
      :class="[
        {
          'faded-overflow-s': showScrollButton.start,
          'faded-overflow-e': showScrollButton.end,
        },
      ]"
    >
      <div
        ref="buttonsRef"
        class="buttons flex justify-start gap-x-3 overflow-x-scroll sm:gap-x-1"
        :class="{
          'ms-11': showScrollButton.start,
          'me-11': showScrollButton.end,
        }"
      >
        <VButton
          v-if="showCreator"
          as="VLink"
          size="small"
          has-icon-start
          class="label-bold"
          :variant="buttonVariant"
          :href="creatorHref"
        >
          <VIcon name="person" /><span class="w-max">{{ creator }}</span>
        </VButton>
        <VButton
          as="VLink"
          size="small"
          has-icon-start
          class="label-bold"
          :variant="buttonVariant"
          :href="sourceHref"
          ><VIcon name="institution" /><span class="w-max">{{
            sourceName
          }}</span>
        </VButton>
      </div>
    </div>
    <div
      v-show="showScrollButton.start"
      class="absolute start-0 z-10 h-8 w-8 flex-none"
    >
      <VIconButton
        :icon-props="{ name: 'chevron-back', rtlFlip: true }"
        label="scroll"
        variant="transparent-gray"
        size="small"
        @click="scroll('toStart')"
      />
    </div>

    <div
      v-show="showScrollButton.end"
      class="absolute end-0 z-10 h-8 w-8 flex-none"
    >
      <VIconButton
        :icon-props="{ name: 'chevron-forward', rtlFlip: true }"
        label="scroll"
        variant="transparent-gray"
        size="small"
        @click="scroll('toEnd')"
      />
    </div>
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

import { useUiStore } from "~/stores/ui"
import { useI18n } from "~/composables/use-i18n"
import type { SupportedMediaType } from "~/constants/media"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

/**
 * A link to a collection page, either a source or a creator.
 */
export default defineComponent({
  name: "VByLine",
  components: { VIconButton, VIcon, VButton },
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

    const uiStore = useUiStore()

    const buttonVariant = computed(() =>
      uiStore.isBreakpoint("sm") ? "transparent-gray" : "filled-gray"
    )

    const showCreator = computed(() => {
      return props.creator && props.creator.toLowerCase() !== "unidentified"
    })

    const i18n = useI18n()
    const dir = computed(() => i18n.localeProperties.dir ?? "ltr")

    const scrollStep = 80 // px to scroll on each click
    const scrollThreshold = 40 // px, distance from edge to show scroll buttons
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

    const scroll = (to: "toStart" | "toEnd") => {
      if (!buttonsRef.value) return
      if (to === "toEnd") {
        showScrollButton.start = true
      }
      if (to === "toStart") {
        showScrollButton.end = true
      }
      const buttons = buttonsRef.value
      let scrollValue = to === "toStart" ? -scrollStep : scrollStep
      if (dir.value === "rtl") {
        scrollValue = -scrollValue
      }
      buttons.scrollBy({ left: scrollValue, behavior: "smooth" })
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
        showScrollButton.start = distFromStart > scrollThreshold
        showScrollButton.end = distFromEnd > scrollThreshold
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

      buttonVariant,
      showCreator,
      shouldScroll,
      showScrollButton,

      creatorHref,
      sourceHref,

      scroll,
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
