<template>
  <div
    ref="containerRef"
    class="relative flex max-w-full sm:-ms-1"
    :class="buttonsMargin"
  >
    <div
      class="buttons-container max-w-full"
      :class="{ [`m${scrollButtonPosition}-10`]: shouldScroll }"
    >
      <div
        ref="buttonsRef"
        class="buttons flex justify-start gap-x-3 overflow-x-scroll sm:gap-x-1"
        :class="{ [`faded-overflow-${scrollButtonPosition}`]: shouldScroll }"
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
      v-if="shouldScroll"
      class="absolute z-10 h-8 w-12 bg-white"
      :class="scrollButton.style"
    >
      <VIconButton
        :icon-props="{ name: scrollButton.icon, rtlFlip: true }"
        label="scroll"
        variant="transparent-gray"
        size="small"
        @click="scroll"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref } from "vue"
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
      return props.creator && props.creator !== "Unidentified"
    })

    const shouldScroll = ref(false)
    const { x } = useScroll(buttonsRef)

    const { width: containerWidth } = useElementSize(containerRef)
    const { width: buttonsWidth } = useElementSize(buttonsRef)
    watchDebounced(
      [buttonsWidth, containerWidth],
      () => {
        shouldScroll.value = buttonsWidth.value >= containerWidth.value
      },
      { debounce: 500 }
    )

    const i18n = useI18n()
    const dir = computed(() => i18n.localeProperties.dir ?? "ltr")
    // end, start
    const scrollButtonPosition = ref<"e" | "s">("e")

    const scroll = () => {
      let scrollValue = x.value ? 0 : buttonsWidth.value
      if (dir.value === "rtl") {
        scrollValue = -scrollValue
      }
      buttonsRef.value?.scroll({
        left: scrollValue,
        behavior: "smooth",
      })
      scrollButtonPosition.value =
        scrollButtonPosition.value === "e" ? "s" : "e"
    }

    watchDebounced(
      x,
      (xValue) => {
        const distFromStart = Math.abs(xValue)
        const distFromEnd =
          (buttonsRef.value?.scrollWidth ?? 0) -
          distFromStart -
          containerWidth.value
        if (distFromEnd < 1) {
          scrollButtonPosition.value = "s"
        } else if (distFromStart < 1) scrollButtonPosition.value = "e"
      },
      { debounce: 100 }
    )

    const buttonsMargin = computed(() => {
      return shouldScroll.value ? `p${scrollButtonPosition.value}-8` : ""
    })

    const scrollButton = computed(() => {
      if (scrollButtonPosition.value === "e") {
        return { style: "end-0 ps-3", icon: "chevron-forward" }
      } else {
        return { style: "start-0 pe-3", icon: "chevron-back" }
      }
    })

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
      buttonsMargin,
      shouldScroll,
      scrollButton,
      scrollButtonPosition,

      creatorHref,
      sourceHref,

      scroll,
    }
  },
})
</script>

<style scoped>
.faded-overflow-e:dir(ltr),
.faded-overflow-s:dir(rtl) {
  mask-image: linear-gradient(90deg, transparent 85%, white);
}
.faded-overflow-e:dir(rtl),
.faded-overflow-s:dir(ltr) {
  mask-image: linear-gradient(90deg, white 15%, transparent);
}
.buttons::-webkit-scrollbar {
  width: 0 !important;
  height: 0 !important;
}
.buttons {
  scrollbar-width: none;
}
</style>
